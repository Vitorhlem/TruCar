from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, cast, Integer, update as sa_update
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import datetime 

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


# --- CORREÇÃO 1: Lógica do item_identifier ---



async def create_inventory_items(
    db: AsyncSession, *, part_id: int, organization_id: int, quantity: int, user_id: int, notes: Optional[str] = None
) -> List[InventoryItem]:
    """Cria itens e os adiciona à sessão, sem commit ou flush."""
    
    # 1. Buscar o maior 'item_identifier' existente PARA ESTE part_id
    stmt = select(func.max(InventoryItem.item_identifier)).where(
        InventoryItem.part_id == part_id
    )
    result = await db.execute(stmt)
    # Se não houver itens (None), começamos do 0
    last_identifier = result.scalars().first() or 0 

    new_items = []
    for i in range(quantity):
        
        # 2. Calcular o novo ID local
        current_identifier = last_identifier + 1 + i
        
        new_item = InventoryItem(
            part_id=part_id,
            organization_id=organization_id,
            status=InventoryItemStatus.DISPONIVEL,
            item_identifier=current_identifier # <-- 3. Atribuir o novo ID local
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
        selectinload(InventoryItem.part) # Carrega a relação com Part
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
    
    # Query base para os itens
    stmt = select(InventoryItem).where(
        InventoryItem.organization_id == organization_id
    ).options(
        selectinload(InventoryItem.part), # Carrega o template (Part)
        selectinload(InventoryItem.installed_on_vehicle) # Carrega o Veículo
    )
    
    # Query base para a contagem
    count_stmt = select(func.count()).select_from(InventoryItem).where(
        InventoryItem.organization_id == organization_id
    )

    # Aplicar filtros (status, partId, vehicleId permanecem iguais)
    if status:
        stmt = stmt.where(InventoryItem.status == status)
        count_stmt = count_stmt.where(InventoryItem.status == status)
    if part_id:
        stmt = stmt.where(InventoryItem.part_id == part_id)
        count_stmt = count_stmt.where(InventoryItem.part_id == part_id)
    if vehicle_id:
        stmt = stmt.where(InventoryItem.installed_on_vehicle_id == vehicle_id)
        count_stmt = count_stmt.where(InventoryItem.installed_on_vehicle_id == vehicle_id)
    
    # Aplicar filtro de busca (procura no nome da Peça OU IDs)
    if search:
        search_term_text = f"%{search.lower()}%"
        
        # Faz o join com a tabela Part para poder filtrar pelo nome
        stmt = stmt.join(Part, Part.id == InventoryItem.part_id)
        count_stmt = count_stmt.join(Part, Part.id == InventoryItem.part_id)
        
        # --- LÓGICA DE BUSCA ATUALIZADA ---
        search_filters = [
            Part.name.ilike(search_term_text) # Busca por nome da peça
        ]
        
        try:
            # Tenta converter o 'search' para um número
            search_id = int(search)
            # Se conseguir, adiciona busca pelo ID Global (item.id)
            search_filters.append(InventoryItem.id == search_id)
            # E também pelo Cód. Item (item_identifier)
            search_filters.append(InventoryItem.item_identifier == search_id)
        except ValueError:
            pass # Não é um número, continua a busca por texto

        stmt = stmt.where(or_(*search_filters))
        count_stmt = count_stmt.where(or_(*search_filters))
        # --- FIM DA LÓGICA ATUALIZADA ---

    # Obter a contagem total (antes de paginar)
    total = (await db.execute(count_stmt)).scalar_one_or_none() or 0
    
    # Obter os itens com paginação e ordenação
    items = (await db.execute(
        stmt.order_by(InventoryItem.part_id, InventoryItem.item_identifier)
            .offset(skip).limit(limit)
    )).scalars().all()
    
    return {"total": total, "items": items}
# --- NOVO: Função para a Página de Detalhes ---
async def get_item_with_details(db: AsyncSession, *, item_id: int, organization_id: int) -> Optional[InventoryItem]:
    """Busca um item serializado e seu histórico completo."""
    stmt = select(InventoryItem).where(
        InventoryItem.id == item_id, 
        InventoryItem.organization_id == organization_id
    ).options(
        selectinload(InventoryItem.part), # Carrega o template (Part)
        selectinload(InventoryItem.transactions).options( # Carrega todas as transações
            selectinload(InventoryTransaction.user),      # e o usuário de cada transação
            selectinload(InventoryTransaction.related_vehicle),
            selectinload(InventoryTransaction.item),      
            selectinload(InventoryTransaction.part_template) 
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()
# --- FIM DA NOVA FUNÇÃO ---


async def change_item_status(
    db: AsyncSession, *, item: InventoryItem, new_status: InventoryItemStatus, 
    user_id: int, vehicle_id: Optional[int] = None, notes: Optional[str] = None
) -> InventoryItem:
    
    # Validação de transição (lógica da nossa primeira correção)
    current_status = item.status
    if current_status == new_status:
        return item
        
    elif new_status == InventoryItemStatus.FIM_DE_VIDA:
        # Esta verificação agora está segura, porque se o status já fosse
        # FIM_DE_VIDA, a função teria retornado no bloco de código acima.
        if current_status not in [InventoryItemStatus.DISPONIVEL, InventoryItemStatus.EM_USO]:
             raise ValueError(f"Item não pode ser descartado pois seu status é '{current_status}'.")
    
    elif current_status != InventoryItemStatus.DISPONIVEL:
         raise ValueError(f"Não é possível alterar o status do item pois ele não está 'Disponível' (status atual: {current_status}).")


    # Mapeamento do tipo de transação para o log
    transaction_type_map = {
        InventoryItemStatus.EM_USO: TransactionType.INSTALACAO,
        InventoryItemStatus.FIM_DE_VIDA: TransactionType.FIM_DE_VIDA
    }
    
    if new_status not in transaction_type_map:
        raise ValueError("Tipo de transação inválido para mudança de status.")

    # Atualiza o item
    item.status = new_status
    
    # Se for "Em Uso", associa ao veículo. Se for "Fim de Vida", desassocia.
    if new_status == InventoryItemStatus.EM_USO:
        item.installed_on_vehicle_id = vehicle_id
        item.installed_at = func.now()
    else:
        # Remove a associação do veículo ao ser descartado
        item.installed_on_vehicle_id = None
        item.installed_at = None
    
    # Cria o registro de log
    log_entry = log_transaction( 
        db=db, item_id=item.id, part_id=item.part_id, user_id=user_id,
        transaction_type=transaction_type_map[new_status],
        notes=notes,
        # Mantém o vehicle_id no log para rastreabilidade
        related_vehicle_id=vehicle_id or item.installed_on_vehicle_id 
    )
    
    db.add(item)
    db.add(log_entry) # Adiciona o log à sessão
    
    # --- LÓGICA DE CRIAÇÃO / DESATIVAÇÃO DO COMPONENTE ---
    
    if new_status == InventoryItemStatus.EM_USO and vehicle_id:
        # Se está entrando "EM USO", cria um novo VehicleComponent
        
        # Garante que 'item.part' (o template) foi carregado
        part_template = item.part 
        if not part_template:
            # Carrega se não estiver presente (fallback, idealmente já vem carregado)
            part_template = await db.get(Part, item.part_id)

        if part_template:
            new_component = VehicleComponent(
                vehicle_id=vehicle_id,
                part_id=part_template.id,
                is_active=True,
                installation_date=func.now(),
                # Associa o componente diretamente à transação que o criou
                inventory_transaction_id=log_entry.id 
            )
            # Precisamos salvar o log_entry primeiro para obter seu ID
            await db.flush() # Salva o log_entry e o item para obter IDs
            
            new_component.inventory_transaction_id = log_entry.id
            db.add(new_component)
            
            # Lógica para adicionar custo (como já existia)
            if part_template.value and part_template.value > 0:
                new_cost = VehicleCost(
                    description=f"Instalação: {part_template.name} (Cód. Item: {item.item_identifier})",
                    amount=part_template.value,
                    date=datetime.date.today(), 
                    cost_type=CostType.PECAS_COMPONENTES, 
                    vehicle_id=vehicle_id,
                    organization_id=item.organization_id
                )
                db.add(new_cost)
        
    elif new_status == InventoryItemStatus.FIM_DE_VIDA:
        # --- ESTA É A NOVA CORREÇÃO ---
        # Se está indo para "FIM DE VIDA", desativa o VehicleComponent ativo
        
        # 1. Encontra a transação de instalação (INSTALACAO ou SAIDA_USO) mais recente deste item
        install_transaction_stmt = select(InventoryTransaction.id).where(
            InventoryTransaction.item_id == item.id,
            or_(
                InventoryTransaction.transaction_type == TransactionType.INSTALACAO,
                InventoryTransaction.transaction_type == TransactionType.SAIDA_USO
            )
        ).order_by(InventoryTransaction.timestamp.desc()).limit(1)
        
        install_transaction_id = (await db.execute(install_transaction_stmt)).scalar_one_or_none()
        
        if install_transaction_id:
            # 2. Desativa o VehicleComponent associado a essa transação
            update_component_stmt = sa_update(VehicleComponent).where(
                VehicleComponent.inventory_transaction_id == install_transaction_id,
                VehicleComponent.is_active == True
            ).values(
                is_active = False,
                uninstallation_date = func.now() # Define a data de remoção/descarte
            )
            await db.execute(update_component_stmt)
            
    # --- FIM DA CORREÇÃO ---

    await db.flush() # Salva todas as alterações pendentes
    return item

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

    # --- GARANTE QUE ESTA LINHA ESTÁ AQUI ---
    stmt = stmt.options(selectinload(InventoryItem.part))
    # --- FIM DA VERIFICAÇÃO ---

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
