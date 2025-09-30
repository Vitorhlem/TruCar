from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime
from typing import List

from app.models.vehicle_component_model import VehicleComponent
from app.models.inventory_transaction_model import TransactionType
from app.schemas.vehicle_component_schema import VehicleComponentCreate
from . import crud_inventory_transaction as crud_transaction
from app.models.vehicle_model import Vehicle # Import explícito

async def install_component(db: AsyncSession, *, vehicle_id: int, user_id: int, organization_id: int, obj_in: VehicleComponentCreate) -> VehicleComponent:
    """
    Instala um componente em um veículo, criando a transação de saída de estoque.
    """
    # Esta função já estava correta, mas a mantemos para integridade do arquivo
    transaction = await crud_transaction.create_transaction(
        db=db,
        part_id=obj_in.part_id,
        user_id=user_id,
        transaction_type=TransactionType.SAIDA_USO,
        quantity_change=-obj_in.quantity,
        notes=f"Instalado no veículo ID {vehicle_id}",
        related_vehicle_id=vehicle_id
    )

    db_obj = VehicleComponent(
        vehicle_id=vehicle_id,
        part_id=obj_in.part_id,
        inventory_transaction_id=transaction.id,
        is_active=True
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def discard_component(db: AsyncSession, *, component_id: int, user_id: int, organization_id: int) -> VehicleComponent:
    """
    Marca um componente como 'descartado' (Fim de Vida) e cria uma transação no histórico.
    """
    stmt = select(VehicleComponent).join(VehicleComponent.vehicle).where(
        VehicleComponent.id == component_id,
        Vehicle.organization_id == organization_id
    )
    result = await db.execute(stmt)
    db_obj = result.scalar_one_or_none()

    if not db_obj:
        raise ValueError("Componente não encontrado ou não pertence à sua organização.")
    
    if not db_obj.is_active:
        raise ValueError("Este componente já foi descartado.")

    db_obj.is_active = False
    db_obj.uninstallation_date = datetime.utcnow()
    db.add(db_obj)
    
    # Adiciona um registro no histórico de movimentações para o descarte
    await crud_transaction.create_transaction(
        db=db,
        part_id=db_obj.part_id,
        user_id=user_id,
        transaction_type=TransactionType.SAIDA_FIM_DE_VIDA,
        quantity_change=0,
        notes=f"Componente descartado (fim de vida) do veículo ID {db_obj.vehicle_id}",
        related_vehicle_id=db_obj.vehicle_id
    )
    
    await db.commit()
    await db.refresh(db_obj, ["part"])
    return db_obj

async def get_components_by_vehicle(db: AsyncSession, *, vehicle_id: int) -> List[VehicleComponent]:
    """
    Busca o histórico de componentes ATIVOS instalados em um veículo.
    """
    stmt = select(VehicleComponent).where(
        VehicleComponent.vehicle_id == vehicle_id,
        VehicleComponent.is_active == True
    ).options(selectinload(VehicleComponent.part)).order_by(VehicleComponent.installation_date.desc())
    
    result = await db.execute(stmt)
    return result.scalars().all()