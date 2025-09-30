from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload 
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List

from app.models.part_model import Part
from app.schemas.vehicle_cost_schema import VehicleCostCreate
from . import crud_inventory_transaction as crud_transaction
from . import crud_vehicle_cost as crud_cost # Importa o CRUD de custos

from app.models.vehicle_component_model import VehicleComponent
from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.schemas.vehicle_component_schema import VehicleComponentCreate
from . import crud_inventory_transaction as crud_transaction
from app.models.vehicle_model import Vehicle
from app.models.vehicle_cost_model import CostType


async def install_component(db: AsyncSession, *, vehicle_id: int, user_id: int, organization_id: int, obj_in: VehicleComponentCreate) -> VehicleComponent:
    """
    Instala um componente, dá baixa no stock, e cria um custo se a peça tiver valor.
    """
    part_to_install = await db.get(Part, obj_in.part_id)
    if not part_to_install:
        raise ValueError("Peça a ser instalada não encontrada no inventário.")
    
    if part_to_install.stock < obj_in.quantity:
        raise ValueError("Estoque insuficiente para instalar esta quantidade.")

    transaction = await crud_transaction.create_transaction(
        db=db,
        part_id=obj_in.part_id,
        user_id=user_id,
        transaction_type=TransactionType.SAIDA_USO,
        quantity_change=-obj_in.quantity,
        notes=f"Instalado no veículo ID {vehicle_id}",
        related_vehicle_id=vehicle_id
    )

    new_component = VehicleComponent(
        vehicle_id=vehicle_id,
        part_id=obj_in.part_id,
        inventory_transaction_id=transaction.id,
        installation_date=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(new_component)

    # --- LÓGICA DE CUSTO CORRIGIDA ---
    if part_to_install.value and part_to_install.value > 0:
        total_cost = part_to_install.value * obj_in.quantity
        cost_in = VehicleCostCreate(
            # 1. Adiciona o campo 'description' obrigatório
            description=f"Custo da instalação de {obj_in.quantity}x '{part_to_install.name}'",
            amount=total_cost,
            date=datetime.now(timezone.utc).date(),
            # 2. Usa o novo tipo de custo do Enum
            cost_type=CostType.PECAS_COMPONENTES
        )
        await crud_cost.create_cost(
            db=db,
            obj_in=cost_in,
            vehicle_id=vehicle_id,
            organization_id=organization_id
        )
    # --- FIM DA CORREÇÃO ---

    await db.commit()
    await db.refresh(new_component, ["part"])

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
    stmt = (
        select(VehicleComponent)
        .where(
            VehicleComponent.vehicle_id == vehicle_id,
            VehicleComponent.is_active == True
        )
        .options(
            # CORREÇÃO: Usamos subqueryload para carregar relações aninhadas
            # Carrega a Peça -> Transação -> Utilizador que fez a transação
            selectinload(VehicleComponent.part),
            subqueryload(VehicleComponent.inventory_transaction).selectinload(
                InventoryTransaction.user
            ),
        )
        .order_by(VehicleComponent.installation_date.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()