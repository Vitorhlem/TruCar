from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload 
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List, Optional # <-- IMPORTAR OPTIONAL

# --- IMPORTS NECESSÁRIOS ---
from app.models.part_model import Part, InventoryItem, InventoryItemStatus
from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.vehicle_model import Vehicle
from app import crud 
from app.models.user_model import User # <--- IMPORTAR O MODELO 'User'

# --- IMPORTS EXISTENTES ---
from app.models.vehicle_component_model import VehicleComponent
from app.schemas.vehicle_component_schema import VehicleComponentCreate
from . import crud_inventory_transaction as crud_transaction


async def get_component_for_api(db: AsyncSession, *, component_id: int) -> Optional[VehicleComponent]:
    """
    Recarrega um componente com todas as relações necessárias
    para o 'response_model' da API.
    """
    stmt = select(VehicleComponent).where(VehicleComponent.id == component_id).options(
        # Carrega Part -> Items (para o schema PartPublic)
        selectinload(VehicleComponent.part).selectinload(Part.items), 
        
        # --- CORREÇÃO AQUI ---
        # Carrega Transação -> Usuário -> Organização
        # Isso satisfaz a cadeia de schemas:
        # VehicleComponentPublic -> TransactionForComponent -> UserPublic -> OrganizationNestedInUser
        selectinload(VehicleComponent.inventory_transaction)
            .selectinload(InventoryTransaction.user)
            .selectinload(User.organization) 
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def install_component(db: AsyncSession, *, vehicle_id: int, user_id: int, organization_id: int, obj_in: VehicleComponentCreate) -> VehicleComponent:
    """
    Instala um componente usando a lógica de item a item.
    NÃO FAZ COMMIT.
    """
    
    # 1. Verifica se a peça (template) existe.
    part_template = await db.get(Part, obj_in.part_id)
    if not part_template:
        raise ValueError("Peça (template) não encontrada no inventário.")
    
    # 2. Encontra o PRIMEIRO item de inventário DISPONÍVEL
    stmt = select(InventoryItem).where(
        InventoryItem.part_id == obj_in.part_id,
        InventoryItem.status == InventoryItemStatus.DISPONIVEL,
        InventoryItem.organization_id == organization_id
    ).limit(1)
    
    result = await db.execute(stmt)
    item_to_install = result.scalars().first()

    if not item_to_install:
        raise ValueError(f"Estoque insuficiente para '{part_template.name}'. Nenhum item disponível.")

    # 3. Chama a função central 'change_item_status'
    updated_item = await crud.crud_part.change_item_status(
        db=db,
        item=item_to_install,
        new_status=InventoryItemStatus.EM_USO,
        user_id=user_id,
        vehicle_id=vehicle_id,
        notes=f"Instalado no veículo ID {vehicle_id}"
    )

    # 4. Encontra o VehicleComponent recém-criado pela 'change_item_status'
    stmt_comp = select(VehicleComponent).join(
        InventoryTransaction, VehicleComponent.inventory_transaction_id == InventoryTransaction.id
    ).where(
        InventoryTransaction.item_id == updated_item.id,
        InventoryTransaction.transaction_type == TransactionType.SAIDA_USO
    ).order_by(InventoryTransaction.timestamp.desc()).limit(1)

    res_comp = await db.execute(stmt_comp)
    new_component = res_comp.scalars().first()
    
    if not new_component:
        raise Exception("Falha ao criar o registro do componente após a instalação.")
    
    # 5. Retorna o componente "sujo" (sem commit) para o endpoint
    return new_component


async def discard_component(db: AsyncSession, *, component_id: int, user_id: int, organization_id: int) -> VehicleComponent:
    """
    Marca um componente como 'descartado' (Fim de Vida) usando a lógica de item a item.
    NÃO FAZ COMMIT.
    """
    
    # 1. Encontra o VehicleComponent e o Item de Inventário associado
    stmt = select(VehicleComponent).where(
        VehicleComponent.id == component_id
    ).options(
        selectinload(VehicleComponent.inventory_transaction).selectinload(InventoryTransaction.item),
        selectinload(VehicleComponent.vehicle) # Para verificação de organização
    )
    
    result = await db.execute(stmt)
    db_component = result.scalar_one_or_none()

    if not db_component:
        raise ValueError("Componente não encontrado.")
    
    if db_component.vehicle.organization_id != organization_id:
         raise ValueError("Componente não pertence à sua organização.")
         
    if not db_component.is_active:
        raise ValueError("Este componente já foi descartado.")
        
    # 2. Encontra o item de inventário original
    inventory_item = db_component.inventory_transaction.item
    if not inventory_item:
        raise ValueError("Item de inventário original não encontrado para este componente.")

    if inventory_item.status != InventoryItemStatus.EM_USO:
         raise ValueError(f"Este item não pode ser descartado (status atual: {inventory_item.status}).")

    # 3. Chama a função central 'change_item_status' para FIM_DE_VIDA
    await crud.crud_part.change_item_status(
        db=db,
        item=inventory_item,
        new_status=InventoryItemStatus.FIM_DE_VIDA,
        user_id=user_id,
        vehicle_id=db_component.vehicle_id, # Mantém a referência do veículo
        notes=f"Componente descartado (fim de vida) do veículo ID {db_component.vehicle_id}"
    )

    # 4. Atualiza o próprio VehicleComponent
    db_component.is_active = False
    db_component.uninstallation_date = datetime.now(timezone.utc)
    db.add(db_component)
    
    await db.flush()
    
    # 5. Retorna o componente "sujo" (sem commit) para o endpoint
    return db_component


async def get_components_by_vehicle(db: AsyncSession, *, vehicle_id: int) -> List[VehicleComponent]:
    """
    Busca o histórico de componentes ATIVOS instalados em um veículo.
    (Esta função também precisa da correção)
    """
    stmt = (
        select(VehicleComponent)
        .where(
            VehicleComponent.vehicle_id == vehicle_id,
            VehicleComponent.is_active == True
        )
        .options(
            selectinload(VehicleComponent.part).selectinload(Part.items),
            
            # --- CORREÇÃO AQUI TAMBÉM ---
            selectinload(VehicleComponent.inventory_transaction)
                .selectinload(InventoryTransaction.user)
                .selectinload(User.organization)
        )
        .order_by(VehicleComponent.installation_date.desc())
    )
    
    result = await db.execute(stmt)
    return result.scalars().all()