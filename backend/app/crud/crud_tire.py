from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.vehicle_model import Vehicle
from app.models.part_model import Part, PartCategory
from app.models.tire_model import VehicleTire
from app.models.inventory_transaction_model import TransactionType
from . import inventory_transaction

async def get_active_tires_by_vehicle(db: AsyncSession, vehicle_id: int):
    """Retorna os pneus ativos atualmente instalados em um veículo."""
    stmt = (
        select(VehicleTire)
        .where(VehicleTire.vehicle_id == vehicle_id, VehicleTire.is_active == True)
        .options(selectinload(VehicleTire.part))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def install_tire(
    db: AsyncSession,
    *,
    vehicle_id: int,
    part_id: int,
    position_code: str,
    install_km: int,
    user_id: int
):
    """Instala um pneu em um veículo e registra a transação de inventário."""
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise ValueError("Veículo não encontrado.")

    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça (pneu) não encontrada.")
    if part.category != PartCategory.PNEU:
        raise ValueError("A peça selecionada não é um pneu.")
    if part.stock <= 0:
        raise ValueError("Pneu sem estoque disponível.")

    stmt = select(VehicleTire).where(
        VehicleTire.vehicle_id == vehicle_id,
        VehicleTire.position_code == position_code,
        VehicleTire.is_active == True
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError(f"A posição {position_code} já está ocupada.")

    new_vehicle_tire = VehicleTire(
        vehicle_id=vehicle_id,
        part_id=part_id,
        position_code=position_code,
        install_km=install_km,
        is_active=True
    )
    db.add(new_vehicle_tire)

    transaction = await inventory_transaction.create_transaction(
        db=db,
        part_id=part_id,
        user_id=user_id,
        transaction_type=TransactionType.INSTALACAO.value,  # CORRIGIDO
        quantity_change=-1,
        notes=f"Instalação do pneu no veículo {vehicle.license_plate or vehicle.identifier} na posição {position_code}",
        related_vehicle_id=vehicle_id
    )

    await db.flush()
    new_vehicle_tire.inventory_transaction_id = transaction.id
    
    await db.commit()
    return new_vehicle_tire

async def remove_tire(
    db: AsyncSession,
    *,
    tire_id: int,
    removal_km: int,
    user_id: int
):
    """Remove um pneu, desativando-o e registrando o descarte."""
    tire_to_remove = await db.get(VehicleTire, tire_id, options=[selectinload(VehicleTire.part)])
    if not tire_to_remove or not tire_to_remove.is_active:
        raise ValueError("Pneu não encontrado ou já foi removido.")
    if removal_km <= tire_to_remove.install_km:
        raise ValueError("O KM de remoção deve ser maior que o KM de instalação.")

    tire_to_remove.is_active = False
    tire_to_remove.removal_km = removal_km
    
    await inventory_transaction.create_transaction(
        db=db,
        part_id=tire_to_remove.part_id,
        user_id=user_id,
        transaction_type=TransactionType.DESCARTE.value,  # CORRIGIDO
        quantity_change=0,
        notes=f"Descarte do pneu (Série: {tire_to_remove.part.serial_number}) removido do veículo ID {tire_to_remove.vehicle_id}",
        related_vehicle_id=tire_to_remove.vehicle_id
    )
    await db.commit()
    return tire_to_remove

