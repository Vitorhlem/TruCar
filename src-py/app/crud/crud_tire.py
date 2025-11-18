from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import datetime
from typing import Optional

from app.models.vehicle_model import Vehicle
from app.models.part_model import Part, PartCategory, InventoryItem, InventoryItemStatus
from app.models.tire_model import VehicleTire
from app.models.inventory_transaction_model import TransactionType
from app.models.vehicle_cost_model import CostType

from . import crud_inventory_transaction
from . import crud_vehicle_cost
from app.schemas.vehicle_cost_schema import VehicleCostCreate


async def get_active_tires_by_vehicle(db: AsyncSession, vehicle_id: int):
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
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise ValueError("Veículo não encontrado.")

    part = await db.get(Part, part_id)
    if not part:
        raise ValueError("Peça (pneu) não encontrada.")
    if part.category != PartCategory.PNEU:
        raise ValueError("A peça selecionada não é um pneu.")

    # 1. Buscar um item DISPONÍVEL específico
    stmt_item = select(InventoryItem).where(
        InventoryItem.part_id == part_id,
        InventoryItem.status == InventoryItemStatus.DISPONIVEL
    ).limit(1)
    
    item_to_install = (await db.execute(stmt_item)).scalar_one_or_none()
    
    if not item_to_install:
        raise ValueError("Pneu sem estoque disponível (Nenhum item 'Disponível' encontrado).")

    # 2. Verificar posição
    stmt = select(VehicleTire).where(
        VehicleTire.vehicle_id == vehicle_id,
        VehicleTire.position_code == position_code,
        VehicleTire.is_active.is_(True)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError(f"A posição {position_code} já está ocupada.")

    # 3. Atualizar status do Item
    item_to_install.status = InventoryItemStatus.EM_USO
    item_to_install.installed_on_vehicle_id = vehicle_id
    db.add(item_to_install)

    # 4. Criar registro do Pneu
    new_vehicle_tire = VehicleTire(
        vehicle_id=vehicle_id,
        part_id=part_id,
        position_code=position_code,
        install_km=install_km,
        install_engine_hours=install_engine_hours,
        is_active=True
    )
    db.add(new_vehicle_tire)

    # 5. Criar Transação (Passando item_id!)
    transaction = await crud_inventory_transaction._create_transaction_no_commit(
        db=db,
        part_id=part_id,
        user_id=user_id,
        transaction_type=TransactionType.INSTALACAO,
        quantity_change=-1, # Ignorado pelo modelo, mas mantido na assinatura
        item_id=item_to_install.id, # <--- OBRIGATÓRIO AGORA
        notes=f"Instalação do pneu (Item {item_to_install.item_identifier}) no veículo {vehicle.license_plate or vehicle.identifier} pos {position_code}",
        related_vehicle_id=vehicle_id
    )
    
    await db.flush()
    new_vehicle_tire.inventory_transaction_id = transaction.id
    
    # 6. Custo
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
            commit=False
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
    tire_to_remove = await db.get(VehicleTire, tire_id, options=[selectinload(VehicleTire.part), selectinload(VehicleTire.vehicle)])
    if not tire_to_remove or not tire_to_remove.is_active:
        raise ValueError("Pneu não encontrado ou já foi removido.")

    # Validações de KM/Horas
    if removal_km < tire_to_remove.install_km:
        raise ValueError("O KM de remoção deve ser maior ou igual ao KM de instalação.")
    calculated_km_run = float(removal_km - tire_to_remove.install_km)

    if removal_engine_hours is not None and tire_to_remove.install_engine_hours is not None:
        if removal_engine_hours < tire_to_remove.install_engine_hours:
            raise ValueError("As Horas do Motor de remoção devem ser maiores ou iguais às de instalação.")
        calculated_km_run = float(removal_engine_hours - tire_to_remove.install_engine_hours)
    
    tire_to_remove.is_active = False
    tire_to_remove.removal_km = removal_km
    tire_to_remove.removal_engine_hours = removal_engine_hours
    tire_to_remove.removal_date = datetime.datetime.now(datetime.timezone.utc)
    tire_to_remove.km_run = calculated_km_run 

    # Encontrar o Item Original através da transação de instalação
    stmt_transaction = select(crud_inventory_transaction.InventoryTransaction).where(
        crud_inventory_transaction.InventoryTransaction.id == tire_to_remove.inventory_transaction_id
    ).options(selectinload(crud_inventory_transaction.InventoryTransaction.item))
    
    origin_transaction = (await db.execute(stmt_transaction)).scalar_one_or_none()
    
    item_id_for_discard = None
    item_note = ""

    if origin_transaction and origin_transaction.item:
        item = origin_transaction.item
        item.status = InventoryItemStatus.FIM_DE_VIDA
        item.installed_on_vehicle_id = None
        db.add(item)
        item_id_for_discard = item.id
        item_note = f"(Item ID: {item.item_identifier})"
    else:
        # Fallback: Se não achou o item (dados antigos?), tenta achar um item EM_USO desse pneu nesse veículo
        # Isso é uma medida de segurança para não quebrar o sistema
        stmt_fallback = select(InventoryItem).where(
            InventoryItem.part_id == tire_to_remove.part_id,
            InventoryItem.installed_on_vehicle_id == tire_to_remove.vehicle_id,
            InventoryItem.status == InventoryItemStatus.EM_USO
        ).limit(1)
        fallback_item = (await db.execute(stmt_fallback)).scalar_one_or_none()
        if fallback_item:
            fallback_item.status = InventoryItemStatus.FIM_DE_VIDA
            fallback_item.installed_on_vehicle_id = None
            db.add(fallback_item)
            item_id_for_discard = fallback_item.id
        else:
             # Se realmente não tiver item (sistema legado), precisaremos criar um "fictício" ou falhar?
             # Como o banco exige item_id, vamos falhar com mensagem clara se não houver consistência.
             raise ValueError("Erro de integridade: Não foi possível encontrar o Item de Inventário associado a este pneu para registrar o descarte.")

    # Criar Transação de Descarte (Passando item_id!)
    await crud_inventory_transaction.create_transaction(
        db=db, 
        part_id=tire_to_remove.part_id,
        user_id=user_id,
        transaction_type=TransactionType.DESCARTE,
        quantity_change=0,
        item_id=item_id_for_discard, # <--- OBRIGATÓRIO
        notes=f"Descarte do pneu {item_note} (Série: {tire_to_remove.part.serial_number}) removido do veículo ID {tire_to_remove.vehicle_id}",
        related_vehicle_id=tire_to_remove.vehicle_id
    )
    
    return tire_to_remove


async def get_removed_tires_for_vehicle(db: AsyncSession, *, vehicle_id: int) -> list[VehicleTire]:
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