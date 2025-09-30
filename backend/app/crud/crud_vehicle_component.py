from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime, timezone # --- ADICIONADO timezone ---
from typing import List

from app.models.vehicle_component_model import VehicleComponent
from app.models.inventory_transaction_model import TransactionType
from app.schemas.vehicle_component_schema import VehicleComponentCreate
from app.schemas.inventory_transaction_schema import TransactionCreate
from . import crud_inventory_transaction as crud_transaction
from app.models.vehicle_model import Vehicle

async def install_component(db: AsyncSession, *, vehicle_id: int, user_id: int, organization_id: int, obj_in: VehicleComponentCreate) -> VehicleComponent:
    """
    Instala um componente em um veículo, criando a transação de saída de estoque.
    """
    install_transaction = TransactionCreate(
        transaction_type=TransactionType.SAIDA_USO,
        quantity=obj_in.quantity,
        notes=f"Instalado no veículo ID {vehicle_id}",
        related_vehicle_id=vehicle_id
    )
    transaction = await crud_transaction.create_transaction(
        db=db,
        part_id=obj_in.part_id,
        user_id=user_id,
        transaction_in=install_transaction
    )
    # A lógica para criar o VehicleComponent foi movida para dentro do create_transaction
    # para garantir a consistência dos dados, então não precisamos recriá-la aqui.
    # Apenas precisamos buscar o componente recém-criado para retorná-lo.
    stmt = select(VehicleComponent).where(VehicleComponent.inventory_transaction_id == transaction.id)
    result = await db.execute(stmt)
    new_component = result.scalar_one()

    return new_component

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
    # --- CORREÇÃO APLICADA AQUI ---
    db_obj.uninstallation_date = datetime.now(timezone.utc)
    db.add(db_obj)
    
    discard_transaction = TransactionCreate(
        transaction_type=TransactionType.SAIDA_FIM_DE_VIDA,
        quantity=0, # Não afeta o estoque, é apenas um registro histórico
        notes=f"Componente descartado (fim de vida) do veículo ID {db_obj.vehicle_id}",
        related_vehicle_id=db_obj.vehicle_id
    )
    await crud_transaction.create_transaction(
        db=db,
        part_id=db_obj.part_id,
        user_id=user_id,
        transaction_in=discard_transaction
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