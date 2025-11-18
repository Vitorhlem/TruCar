from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, Integer, update as sa_update
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import datetime 

# Imports necessários para a correção
from app.models.vehicle_component_model import VehicleComponent
from app.models.vehicle_cost_model import VehicleCost, CostType
from app.models.inventory_transaction_model import InventoryTransaction
from app.models.vehicle_model import Vehicle 
from app.crud.crud_user import count_by_org
from app.models.part_model import Part, InventoryItem, InventoryItemStatus, PartCategory
from . import crud_inventory_transaction as crud_transaction
from app.schemas.part_schema import PartCreate, PartUpdate
from app.models.inventory_transaction_model import TransactionType

def log_transaction(
    db: AsyncSession, *, item_id: int, part_id: int, user_id: int, 
    transaction_type: TransactionType, notes: Optional[str] = None, 
    related_vehicle_id: Optional[int] = None
) -> InventoryTransaction:
    log_entry = InventoryTransaction(
        item_id=item_id,
        part_id=part_id,
        user_id=user_id,
        transaction_type=transaction_type,
        notes=notes,
        related_vehicle_id=related_vehicle_id
    )
    return log_entry


# --- (Funções create_inventory_items, get_item_by_id, get_all_items_paginated, get_item_with_details permanecem iguais) ---

async def create_inventory_items(
    db: AsyncSession, *, part_id: int, organization_id: int, quantity: int, user_id: int, notes: Optional[str] = None
) -> List[InventoryItem]:
    """Cria itens e os adiciona à sessão, sem commit ou flush."""
    
    stmt = select(func.max(InventoryItem.item_identifier)).where(
        InventoryItem.part_id == part_id
    )
    result = await db.execute(stmt)
    last_identifier = result.scalars().first() or 0 

    new_items = []
    for i in range(quantity):
        current_identifier = last_identifier + 1 + i
        
        new_item = InventoryItem(
            part_id=part_id,
            organization_id=organization_id,
            status=InventoryItemStatus.DISPONIVEL,
            item_identifier=current_identifier
        )
        db.add(new_item)
        new_items.append(new_item)
    
    await db.flush() 

    for new_item in new_items:
        log = log_transaction(
            db=db, item_id=new_item.id, part_id=part_id, user_id=user_id,
            transaction_type=TransactionType.ENTRADA,
            notes=notes or "Entrada de novo item"
        )
        db.add(log)
        
    return new_items

async def get_item_by_id(db: AsyncSession, *, item_id: int, organization_id: int) -> Optional[InventoryItem]:
    """Busca um item serializado específico e os dados da peça (part) associada."""
    stmt = select(InventoryItem).where(
        InventoryItem.id == item_id, 
        InventoryItem.organization_id == organization_id
    ).options(
        selectinload(InventoryItem.part) 
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_all_items_paginated(
    db: AsyncSession, *, 
    organization_id: int, 
    skip: int, 
    limit: int, 
    status: Optional[InventoryItemStatus] = None, 
    part_id: Optional[int] = None, 
    vehicle_id: Optional[int] = None,
    search: Optional[str] = None
):
    """
    Busca todos os InventoryItems de forma paginada, com filtros.
    """
    
    stmt = select(InventoryItem).where(
        InventoryItem.organization_id == organization_id
    ).options(
        selectinload(InventoryItem.part), 
        selectinload(InventoryItem.installed_on_vehicle) 
    )
    
    count_stmt = select(func.count()).select_from(InventoryItem).where(
        InventoryItem.organization_id == organization_id
    )

    if status:
        stmt = stmt.where(InventoryItem.status == status)
        count_stmt = count_stmt.where(InventoryItem.status == status)
    if part_id:
        stmt = stmt.where(InventoryItem.part_id == part_id)
        count_stmt = count_stmt.where(InventoryItem.part_id == part_id)
    if vehicle_id:
        stmt = stmt.where(InventoryItem.installed_on_vehicle_id == vehicle_id)
        count_stmt = count_stmt.where(InventoryItem.installed_on_vehicle_id == vehicle_id)
    
    if search:
        search_term_text = f"%{search.lower()}%"
        
        stmt = stmt.join(Part, Part.id == InventoryItem.part_id)
        count_stmt = count_stmt.join(Part, Part.id == InventoryItem.part_id)
        
        search_filters = [
            Part.name.ilike(search_term_text) 
        ]
        
        try:
            search_id = int(search)
            search_filters.append(InventoryItem.id == search_id)
            search_filters.append(InventoryItem.item_identifier == search_id)
        except ValueError:
            pass 

        stmt = stmt.where(or_(*search_filters))
        count_stmt = count_stmt.where(or_(*search_filters))

    total = (await db.execute(count_stmt)).scalar_one_or_none() or 0
    
    items = (await db.execute(
        stmt.order_by(InventoryItem.part_id, InventoryItem.item_identifier)
            .offset(skip).limit(limit)
    )).scalars().all()
    
    return {"total": total, "items": items}

async def get_item_with_details(db: AsyncSession, *, item_id: int, organization_id: int) -> Optional[InventoryItem]:
    """Busca um item serializado e seu histórico completo."""
    stmt = select(InventoryItem).where(
        InventoryItem.id == item_id, 
        InventoryItem.organization_id == organization_id
    ).options(
        selectinload(InventoryItem.part), 
        selectinload(InventoryItem.transactions).options( 
            selectinload(InventoryTransaction.user),       
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.item),      
            selectinload(InventoryTransaction.part_template) 
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()

# ---
# --- FUNÇÃO CENTRAL CORRIGIDA
# ---
async def change_item_status(
    db: AsyncSession, *, item: InventoryItem, new_status: InventoryItemStatus, 
    user_id: int, vehicle_id: Optional[int] = None, notes: Optional[str] = None
) -> InventoryItem:
    
    # Validação de transição
    current_status = item.status
    if current_status == new_status:
        return item
        
    # --- LÓGICA DE VALIDAÇÃO ATUALIZADA (mais robusta) ---
    if new_status == InventoryItemStatus.EM_USO:
        if current_status != InventoryItemStatus.DISPONIVEL:
            raise ValueError(f"Não é possível instalar o item pois ele não está 'Disponível' (status atual: {current_status}).")
        if not vehicle_id:
            raise ValueError("vehicle_id é obrigatório para instalar um item (EM_USO).")
            
    elif new_status == InventoryItemStatus.FIM_DE_VIDA:
        if current_status not in [InventoryItemStatus.DISPONIVEL, InventoryItemStatus.EM_USO]:
             raise ValueError(f"Item não pode ser descartado pois seu status é '{current_status}'.")
             
    elif new_status == InventoryItemStatus.DISPONIVEL:
         if current_status not in [InventoryItemStatus.EM_USO, InventoryItemStatus.FIM_DE_VIDA]:
               raise ValueError(f"Item não pode ser retornado ao estoque (status atual: {current_status}).")
    # --- FIM DA VALIDAÇÃO ---


    # Mapeamento do tipo de transação para o log
    transaction_type_map = {
        InventoryItemStatus.EM_USO: TransactionType.INSTALACAO,
        InventoryItemStatus.FIM_DE_VIDA: TransactionType.FIM_DE_VIDA,
        InventoryItemStatus.DISPONIVEL: TransactionType.ENTRADA # Usado para retorno ao estoque
    }
    
    transaction_type = transaction_type_map.get(new_status)
    
    if current_status == InventoryItemStatus.EM_USO:
        if new_status == InventoryItemStatus.FIM_DE_VIDA:
            transaction_type = TransactionType.FIM_DE_VIDA
        elif new_status == InventoryItemStatus.DISPONIVEL:
            transaction_type = TransactionType.ENTRADA 
    
    if not transaction_type:
         raise ValueError("Tipo de transação inválido para mudança de status.")

    # Atualiza o item
    item.status = new_status
    
    if new_status == InventoryItemStatus.EM_USO:
        item.installed_on_vehicle_id = vehicle_id
        item.installed_at = func.now()
    else:
        item.installed_on_vehicle_id = None
        item.installed_at = None
    
    # Cria o registro de log
    log_entry = log_transaction( 
        db=db, item_id=item.id, part_id=item.part_id, user_id=user_id,
        transaction_type=transaction_type,
        notes=notes,
        related_vehicle_id=vehicle_id or item.installed_on_vehicle_id 
    )
    
    db.add(item)
    db.add(log_entry) 
    
    # Carrega a 'part' (template) para obter o valor
    part_template = item.part 
    if not part_template:
        part_template = await db.get(Part, item.part_id)

    # --- LÓGICA DE CRIAÇÃO / DESATIVAÇÃO DO COMPONENTE E CUSTO (CORRIGIDA) ---
    
    if new_status == InventoryItemStatus.EM_USO and vehicle_id:
        # --- LÓGICA DE INSTALAÇÃO ---
        
        # 1. Flush para obter o ID do log_entry
        await db.flush() 
        
        # 2. Verificar se é re-instalação (procura componente inativo PARA ESTE ITEM)
        stmt_find_old = select(VehicleComponent).join(
            InventoryTransaction, VehicleComponent.inventory_transaction_id == InventoryTransaction.id
        ).where(
            InventoryTransaction.item_id == item.id,
            VehicleComponent.vehicle_id == vehicle_id,
            VehicleComponent.is_active == False
        ).order_by(VehicleComponent.uninstallation_date.desc()).limit(1)
        
        result = await db.execute(stmt_find_old)
        existing_inactive_component = result.scalars().first()

        if existing_inactive_component:
            # --- É UMA RE-INSTALAÇÃO (Ex: Reversão de Peça A) ---
            existing_inactive_component.is_active = True
            existing_inactive_component.uninstallation_date = None
            # Atualiza o ID da transação para a *nova* transação de instalação
            existing_inactive_component.inventory_transaction_id = log_entry.id
            db.add(existing_inactive_component)
            
            # *** NÃO ADICIONA CUSTO ***
            # O custo original já foi pago e nunca foi estornado (porque foi FIM_DE_VIDA).
        
        else:
            # --- É UMA INSTALAÇÃO NOVA ---
            new_component = VehicleComponent(
                vehicle_id=vehicle_id,
                part_id=part_template.id,
                is_active=True,
                installation_date=func.now(),
                inventory_transaction_id=log_entry.id 
            )
            db.add(new_component)
            
            # Adiciona Custo POSITIVO (Débito)
            if part_template.value and part_template.value > 0:
                new_cost = VehicleCost(
                    description=f"Instalação: {part_template.name} (Cód. Item: {item.item_identifier})",
                    amount=part_template.value, # Valor positivo
                    date=datetime.date.today(), 
                    cost_type=CostType.PECAS_COMPONENTES, 
                    vehicle_id=vehicle_id,
                    organization_id=item.organization_id
                )
                db.add(new_cost)

    elif current_status == InventoryItemStatus.EM_USO:
        # --- LÓGICA DE DESINSTALAÇÃO ---
        
        # 1. Encontra a transação de instalação
        install_transaction_stmt = select(InventoryTransaction.id).where(
            InventoryTransaction.item_id == item.id,
            or_(
                InventoryTransaction.transaction_type == TransactionType.INSTALACAO,
                InventoryTransaction.transaction_type == TransactionType.SAIDA_USO
            )
        ).order_by(InventoryTransaction.timestamp.desc()).limit(1)
        
        install_transaction_id = (await db.execute(install_transaction_stmt)).scalar_one_or_none()
        
        if install_transaction_id:
            # 2. Desativa o VehicleComponent
            update_component_stmt = sa_update(VehicleComponent).where(
                VehicleComponent.inventory_transaction_id == install_transaction_id,
                VehicleComponent.is_active == True
            ).values(
                is_active = False,
                uninstallation_date = func.now()
            )
            await db.execute(update_component_stmt)
        
        # --- LÓGICA DE CUSTO (Crédito/Estorno) ---
        if new_status == InventoryItemStatus.DISPONIVEL:
            # Só estorna o custo se voltar ao estoque (Engano / Reversão de Peça B)
            if part_template and part_template.value and part_template.value > 0:
                
                cost_vehicle_id = vehicle_id or item.installed_on_vehicle_id
                
                if cost_vehicle_id:
                    description = f"Retorno Estoque (Estorno): {part_template.name} (Cód. Item: {item.item_identifier})"

                    new_cost = VehicleCost(
                        description=description,
                        amount= -part_template.value, # <-- Valor negativo (Crédito)
                        date=datetime.date.today(), 
                        cost_type=CostType.PECAS_COMPONENTES, 
                        vehicle_id=cost_vehicle_id,
                        organization_id=item.organization_id
                    )
                    db.add(new_cost)
        
        # Se o new_status for FIM_DE_VIDA, NENHUM estorno é criado.
        # O custo da instalação original permanece no veículo, o que está correto.
            
    # --- FIM DA LÓGICA DO COMPONENTE E CUSTO ---

    await db.flush() 
    return item

# --- (Funções get_simple, get_part_with_stock, get_multi_by_org, get_items_for_part, create, update, remove permanecem iguais) ---

async def get_simple(db: AsyncSession, *, part_id: int, organization_id: int) -> Optional[Part]:
    stmt = select(Part).where(Part.id == part_id, Part.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalars().first()
    
async def get_part_with_stock(db: AsyncSession, *, part_id: int, organization_id: int) -> Optional[Part]:
    stmt = (
        select(Part)
        .where(Part.id == part_id, Part.organization_id == organization_id)
        .options(
            selectinload(Part.items) 
        )
    )
    part = (await db.execute(stmt)).scalars().first()
    
    if part:
        part.stock = sum(1 for item in part.items if item.status == InventoryItemStatus.DISPONIVEL)
    return part


async def get_multi_by_org(
    db: AsyncSession,
    *,
    organization_id: int,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Part]:
    
    subquery = (
        select(
            InventoryItem.part_id,
            func.count(InventoryItem.id).label("stock_count")
        )
        .where(InventoryItem.status == InventoryItemStatus.DISPONIVEL)
        .group_by(InventoryItem.part_id)
    ).subquery()

    stmt = (
        select(Part, func.coalesce(subquery.c.stock_count, 0))
        .outerjoin(subquery, Part.id == subquery.c.part_id)
        .where(Part.organization_id == organization_id)
    )

    if search:
        search_term = f"%{search.lower()}%"
        stmt = stmt.where(
            or_(
                Part.name.ilike(search_term),
                Part.brand.ilike(search_term),
                Part.part_number.ilike(search_term)
            )
        )
    
    stmt = stmt.order_by(Part.name).offset(skip).limit(limit)
    
    result_rows = (await db.execute(stmt)).all()

    parts_with_stock = []
    for part, stock_count in result_rows:
        part.stock = stock_count 
        parts_with_stock.append(part)
        
    return parts_with_stock

async def get_items_for_part(
    db: AsyncSession,
    *,
    part_id: int,
    status: Optional[InventoryItemStatus] = None
) -> List[InventoryItem]:
    stmt = select(InventoryItem).where(InventoryItem.part_id == part_id)
    if status:
        stmt = stmt.where(InventoryItem.status == status)

    stmt = stmt.options(selectinload(InventoryItem.part))

    items = (await db.execute(stmt.order_by(InventoryItem.item_identifier))).scalars().all()
    return items

async def create(db: AsyncSession, *, part_in: PartCreate, organization_id: int, user_id: int, photo_url: Optional[str] = None, invoice_url: Optional[str] = None) -> Part:
    initial_quantity = part_in.initial_quantity
    part_data = part_in.model_dump(exclude={"initial_quantity"})

    db_obj = Part(
        **part_data,
        photo_url=photo_url,
        invoice_url=invoice_url,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.flush() 

    if initial_quantity and initial_quantity > 0:
        await create_inventory_items(
            db=db,
            part_id=db_obj.id,
            organization_id=organization_id,
            quantity=initial_quantity,
            user_id=user_id,
            notes=f"Carga inicial de {initial_quantity} itens no sistema."
        )
    
    return db_obj

async def update(db: AsyncSession, *, db_obj: Part, obj_in: PartUpdate, photo_url: Optional[str], invoice_url: Optional[str]) -> Part:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db_obj.photo_url = photo_url
    db_obj.invoice_url = invoice_url 
    
    db.add(db_obj)
    await db.flush()
    return db_obj

async def remove(db: AsyncSession, *, id: int, organization_id: int) -> Optional[Part]:
    db_obj = await get_simple(db, part_id=id, organization_id=organization_id)
    if db_obj:
        await db.delete(db_obj)
    return db_obj

async def count(db: AsyncSession, *, organization_id: int) -> int:
    """Conta o número total de modelos de peças (Part) da organização."""
    stmt = select(func.count(Part.id)).where(Part.organization_id == organization_id)
    result = await db.execute(stmt)
    return result.scalar_one()