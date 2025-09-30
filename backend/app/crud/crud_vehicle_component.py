from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List

from app.models.vehicle_component_model import VehicleComponent
from app.models.inventory_transaction_model import TransactionType
from app.schemas.vehicle_component_schema import VehicleComponentCreate
from . import crud_inventory_transaction as crud_transaction
from app.models.vehicle_model import Vehicle

async def install_component(db: AsyncSession, *, vehicle_id: int, user_id: int, organization_id: int, obj_in: VehicleComponentCreate) -> VehicleComponent:
    """
    Instala um componente em um veículo, dando baixa no estoque e criando o registro do componente.
    """
    # 1. Cria a transação de saída do estoque primeiro
    #    A quantidade de saída é sempre negativa
    transaction = await crud_transaction.create_transaction(
        db=db,
        part_id=obj_in.part_id,
        user_id=user_id,
        transaction_type=TransactionType.SAIDA_USO,
        quantity_change=-obj_in.quantity, # CORREÇÃO: Quantidade negativa para saídas
        notes=f"Instalado no veículo ID {vehicle_id}",
        related_vehicle_id=vehicle_id
    )

    # 2. Cria o registro do componente ativo no veículo
    #    Esta parte estava em falta no seu código original.
    new_component = VehicleComponent(
        vehicle_id=vehicle_id,
        part_id=obj_in.part_id,
        inventory_transaction_id=transaction.id, # Associa o componente à transação
        installation_date=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(new_component)
    await db.commit()
    await db.refresh(new_component, ["part"]) # Carrega os dados da peça para o retorno

    return new_component


async def discard_component(db: AsyncSession, *, component_id: int, user_id: int, organization_id: int) -> VehicleComponent:
    """
    Marca um componente como 'descartado' (Fim de Vida) e cria uma transação de registo.
    """
    stmt = select(VehicleComponent).join(VehicleComponent.vehicle).where(
        VehicleComponent.id == component_id,
        Vehicle.organization_id == organization_id
    ).options(selectinload(VehicleComponent.part)) # Pré-carrega a peça
    result = await db.execute(stmt)
    db_obj = result.scalar_one_or_none()

    if not db_obj:
        raise ValueError("Componente não encontrado ou não pertence à sua organização.")
    
    if not db_obj.is_active:
        raise ValueError("Este componente já foi descartado.")

    db_obj.is_active = False
    db_obj.uninstallation_date = datetime.now(timezone.utc)
    db.add(db_obj)
    
    # Cria a transação de registo do descarte
    await crud_transaction.create_transaction(
        db=db,
        part_id=db_obj.part_id,
        user_id=user_id,
        transaction_type=TransactionType.SAIDA_FIM_DE_VIDA,
        quantity_change=0, # CORREÇÃO: Descarte não altera o estoque
        notes=f"Componente '{db_obj.part.name}' descartado (fim de vida) do veículo ID {db_obj.vehicle_id}",
        related_vehicle_id=db_obj.vehicle_id
    )
    
    await db.commit()
    await db.refresh(db_obj)
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