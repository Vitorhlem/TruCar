from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import datetime
from typing import Optional

# Importações de modelos
from app.models.vehicle_model import Vehicle
from app.models.part_model import Part, PartCategory
from app.models.tire_model import VehicleTire
from app.models.inventory_transaction_model import TransactionType
from app.models.vehicle_cost_model import CostType

# Importações de CRUDs
from . import crud_inventory_transaction
from . import crud_vehicle_cost

# Importações de Schemas
from app.schemas.vehicle_cost_schema import VehicleCostCreate


async def get_active_tires_by_vehicle(db: AsyncSession, vehicle_id: int):
    """Retorna os pneus ativos atualmente instalados em um veículo."""
    stmt = (
        select(VehicleTire)
        .where(VehicleTire.vehicle_id == vehicle_id, VehicleTire.is_active.is_(True))
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
    user_id: int,
    install_engine_hours: Optional[float] = None
):
    """Instala um pneu em um veículo, registra a transação e o custo em uma única transação."""
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
        VehicleTire.is_active.is_(True)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError(f"A posição {position_code} já está ocupada.")

    new_vehicle_tire = VehicleTire(
        vehicle_id=vehicle_id,
        part_id=part_id,
        position_code=position_code,
        install_km=install_km,
        install_engine_hours=install_engine_hours,
        is_active=True
    )
    db.add(new_vehicle_tire)

    # A função _create_transaction_no_commit espera um Enum, não a string
    transaction = await crud_inventory_transaction._create_transaction_no_commit(
        db=db,
        part_id=part_id,
        user_id=user_id,
        transaction_type=TransactionType.INSTALACAO,
        quantity_change=-1,
        notes=f"Instalação do pneu no veículo {vehicle.license_plate or vehicle.identifier} na posição {position_code}",
        related_vehicle_id=vehicle_id
    )
    # Aguarda o flush para que o ID da transação esteja disponível
    await db.flush()
    new_vehicle_tire.inventory_transaction_id = transaction.id
    
    if part.value and part.value > 0:
        cost_in = VehicleCostCreate(
            description=f"Custo de instalação do pneu: {part.brand or ''} {part.name}",
            amount=part.value,
            date=datetime.date.today(),
            cost_type=CostType.PNEU
        )
        await crud_vehicle_cost.create_cost(
            db=db,
            obj_in=cost_in,
            vehicle_id=vehicle_id,
            organization_id=vehicle.organization_id,
            commit=False # Não faz o commit aqui
        )
    
    await db.commit()
    await db.refresh(new_vehicle_tire)
    return new_vehicle_tire

async def remove_tire(
    db: AsyncSession,
    *,
    tire_id: int,
    removal_km: int,
    user_id: int,
    removal_engine_hours: Optional[float] = None
):
    """Remove um pneu, desativando-o e registrando o descarte."""
    tire_to_remove = await db.get(VehicleTire, tire_id, options=[selectinload(VehicleTire.part)])
    if not tire_to_remove or not tire_to_remove.is_active:
        raise ValueError("Pneu não encontrado ou já foi removido.")
    if removal_km < tire_to_remove.install_km:
        raise ValueError("O KM de remoção deve ser maior ou igual ao KM de instalação.")

    tire_to_remove.is_active = False
    tire_to_remove.removal_km = removal_km
    tire_to_remove.removal_engine_hours = removal_engine_hours
    tire_to_remove.removal_date = datetime.datetime.now(datetime.timezone.utc)
    
    # Esta função faz o commit final
    await crud_inventory_transaction.create_transaction(
        db=db, 
        part_id=tire_to_remove.part_id,
        user_id=user_id,
        transaction_type=TransactionType.DESCARTE,
        quantity_change=0, # Descarte não afeta o estoque geral
        notes=f"Descarte do pneu (Série: {tire_to_remove.part.serial_number}) removido do veículo ID {tire_to_remove.vehicle_id}",
        related_vehicle_id=tire_to_remove.vehicle_id
    )
    
    return tire_to_remove


async def get_removed_tires_for_vehicle(db: AsyncSession, *, vehicle_id: int) -> list[VehicleTire]:
    """
    Busca todos os pneus que já foram instalados e removidos de um veículo.
    """
    stmt = (
        select(VehicleTire)
        .where(
            VehicleTire.vehicle_id == vehicle_id,
            VehicleTire.is_active == False,
            VehicleTire.removal_date.isnot(None)
        )
        .options(selectinload(VehicleTire.part))
        .order_by(VehicleTire.removal_date.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()