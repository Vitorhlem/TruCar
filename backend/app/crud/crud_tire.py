from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from datetime import datetime, timezone
from typing import List

from app.models.vehicle_model import Vehicle
from app.models.part_model import Part
from app.models.tire_model import VehicleTire
from app.schemas.inventory_transaction_schema import TransactionCreate
from app.models.inventory_transaction_model import TransactionType
from . import crud_inventory_transaction as crud_transaction

async def get_active_tires_by_vehicle(db: AsyncSession, *, vehicle_id: int) -> List[VehicleTire]:
    """Busca a configuração de pneus ATIVOS para um veículo."""
    stmt = select(VehicleTire).where(
        VehicleTire.vehicle_id == vehicle_id,
        VehicleTire.is_active == 1
    ).options(selectinload(VehicleTire.part))
    
    result = await db.execute(stmt)
    return result.scalars().all()

async def install_tire(db: AsyncSession, *, vehicle_id: int, part_id: int, position_code: str, install_km: int, user_id: int):
    """Instala um pneu em um veículo, dando baixa no estoque."""
    # 1. Verifica se a posição já está ocupada
    stmt_pos = select(VehicleTire).where(VehicleTire.vehicle_id == vehicle_id, VehicleTire.position_code == position_code, VehicleTire.is_active == 1)
    result_pos = await db.execute(stmt_pos)
    if result_pos.scalar_one_or_none():
        raise ValueError(f"A posição {position_code} já está ocupada.")

    # 2. Dá baixa no estoque do pneu
    install_transaction = TransactionCreate(
        transaction_type=TransactionType.SAIDA_USO,
        quantity=1,
        notes=f"Pneu instalado no veículo ID {vehicle_id} na posição {position_code}",
        related_vehicle_id=vehicle_id
    )
    await crud_transaction.create_transaction(db=db, part_id=part_id, user_id=user_id, transaction_in=install_transaction)

    # 3. Cria o registro do pneu no veículo
    db_obj = VehicleTire(
        vehicle_id=vehicle_id,
        part_id=part_id,
        position_code=position_code,
        install_km=install_km
    )
    db.add(db_obj)
    await db.commit()
    return db_obj


async def remove_tire(db: AsyncSession, *, tire_id: int, removal_km: int, user_id: int):
    """Remove (descarta) um pneu de um veículo, calculando o KM rodado."""
    db_tire = await db.get(VehicleTire, tire_id, options=[selectinload(VehicleTire.vehicle)])
    if not db_tire or not db_tire.is_active:
        raise ValueError("Pneu não encontrado ou já foi removido.")
    
    if removal_km < db_tire.install_km:
        raise ValueError("O KM de remoção não pode ser menor que o KM de instalação.")

    # Calcula o KM rodado
    total_km_run = removal_km - db_tire.install_km

    # Atualiza o registro do pneu
    db_tire.is_active = 0
    db_tire.removal_date = datetime.now(timezone.utc)
    db_tire.removal_km = removal_km
    db_tire.total_km_run = total_km_run
    
    # Registra o descarte no histórico de movimentações
    discard_transaction = TransactionCreate(
        transaction_type=TransactionType.SAIDA_FIM_DE_VIDA,
        quantity=0, # Não afeta mais o estoque
        notes=f"Pneu descartado do veículo ID {db_tire.vehicle_id} da posição {db_tire.position_code}. Rodou {total_km_run} km.",
        related_vehicle_id=db_tire.vehicle_id
    )
    await crud_transaction.create_transaction(db=db, part_id=db_tire.part_id, user_id=user_id, transaction_in=discard_transaction)

    await db.commit()
    return db_tire