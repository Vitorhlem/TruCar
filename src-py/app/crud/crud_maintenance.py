from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, cast, Integer, func # <--- ADICIONADO func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, timezone, date # <--- ADICIONADO date

# --- IMPORTS NECESSÁRIOS ---
from app.models.vehicle_component_model import VehicleComponent
from app.models.maintenance_model import (
    MaintenanceRequest, 
    MaintenanceComment, 
    MaintenancePartChange,
    MaintenanceServiceItem, 
    MaintenanceStatus
)
from app.models.vehicle_model import Vehicle
from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.user_model import User
from app.models.part_model import Part, InventoryItem, InventoryItemStatus
from app.schemas.maintenance_schema import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceCommentCreate,
    ReplaceComponentPayload, ReplaceComponentResponse,
    InstallComponentPayload
)
from app import crud
# --- FIM DOS IMPORTS ---


# --- FUNÇÃO create_request ---
async def create_request(
    db: AsyncSession, *, request_in: MaintenanceRequestCreate, reporter_id: int, organization_id: int
) -> MaintenanceRequest:
    """Cria uma nova solicitação de manutenção e retorna o objeto completo."""
    vehicle = await db.get(Vehicle, request_in.vehicle_id)
    if not vehicle or vehicle.organization_id != organization_id:
        raise ValueError("Veículo não encontrado nesta organização.")

    db_obj = MaintenanceRequest(**request_in.model_dump(), reported_by_id=reporter_id, organization_id=organization_id)
    db.add(db_obj)
    
    await db.flush() 
    
    request_id = db_obj.id
    org_id = db_obj.organization_id
    
    await db.commit()
    
    loaded_request = await get_request(db, request_id=request_id, organization_id=org_id)
    if not loaded_request:
        raise Exception("Falha ao recarregar o chamado após a criação.")
        
    return loaded_request


# --- FUNÇÃO DE SUBSTITUIÇÃO ---
async def perform_component_replacement(
    db: AsyncSession, 
    *, 
    request_id: int, 
    payload: ReplaceComponentPayload, 
    user: User
) -> Tuple[MaintenancePartChange, MaintenanceComment, Optional[int]]: 
    
    # 1. Validar o chamado
    request = await db.get(MaintenanceRequest, request_id)
    if not request or request.organization_id != user.organization_id:
        raise ValueError("Chamado de manutenção não encontrado.")
    if not request.vehicle_id:
        raise ValueError("Chamado não está associado a um veículo.")
        
    vehicle_id = request.vehicle_id
    organization_id = user.organization_id
    reported_by_id = request.reported_by_id 

    # 2. Obter e Desinstalar o COMPONENTE ANTIGO
    component_to_remove = await db.get(VehicleComponent, payload.component_to_remove_id)
    if not component_to_remove:
        raise ValueError(f"Componente a ser removido (ID: {payload.component_to_remove_id}) não encontrado.")
    if not component_to_remove.is_active:
        raise ValueError("Este componente já foi removido/descartado.")
    if component_to_remove.vehicle_id != vehicle_id:
        raise ValueError("Este componente não pertence ao veículo do chamado.")

    try:
        uninstalled_component = await crud.crud_vehicle_component.discard_component(
            db=db,
            component_id=component_to_remove.id,
            user_id=user.id,
            organization_id=organization_id,
            final_status=payload.old_item_status, 
            notes=payload.notes                      
        )
    except Exception as e:
        raise e

    # 3. LÓGICA DE INSTALAÇÃO
    new_item = await crud.crud_part.get_item_by_id(db, item_id=payload.new_item_id, organization_id=organization_id)
    if not new_item:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não encontrado.")
    if new_item.status != InventoryItemStatus.DISPONIVEL:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não está 'Disponível'. Status atual: {new_item.status}")

    try:
        install_notes = f"Instalado via Chamado #{request_id}"
        if payload.notes:
            install_notes = f"{payload.notes} ({install_notes})"

        updated_item = await crud.part.change_item_status(
            db=db,
            item=new_item,
            new_status=InventoryItemStatus.EM_USO,
            user_id=user.id,
            vehicle_id=vehicle_id,
            notes=install_notes 
        )
    except Exception as e:
        raise e

    stmt_comp = select(VehicleComponent).join(
        InventoryTransaction, VehicleComponent.inventory_transaction_id == InventoryTransaction.id
    ).where(
        InventoryTransaction.item_id == updated_item.id,
        InventoryTransaction.transaction_type == TransactionType.INSTALACAO
    ).order_by(InventoryTransaction.timestamp.desc()).limit(1)

    res_comp = await db.execute(stmt_comp)
    new_component = res_comp.scalars().first()
    
    if not new_component:
        raise Exception("Falha ao encontrar o registro do componente após a instalação (erro no crud_maintenance).")

    
    # 4. CARREGAR RELAÇÕES PARA O LOG (Para o Cód. Item)
    await db.refresh(uninstalled_component, ["part", "inventory_transaction"])
    if uninstalled_component.inventory_transaction:
        await db.refresh(uninstalled_component.inventory_transaction, ["item"])
    
    old_part_name = uninstalled_component.part.name
    old_item_identifier = uninstalled_component.inventory_transaction.item.item_identifier

    await db.refresh(new_component, ["part", "inventory_transaction"])
    if new_component.inventory_transaction:
        await db.refresh(new_component.inventory_transaction, ["item"])

    new_part_name = new_component.part.name
    new_item_identifier = new_component.inventory_transaction.item.item_identifier

    # 5. Criar o LOG ESTRUTURADO (MaintenancePartChange)
    db_log = MaintenancePartChange(
        maintenance_request_id=request_id,
        user_id=user.id,
        notes=payload.notes,
        component_removed_id=uninstalled_component.id,
        component_installed_id=new_component.id
    )
    db.add(db_log)
    
    # 6. Criar o COMENTÁRIO de log (human-readable)
    comment_text = (
        f"Substituição de componente realizada por {user.full_name}:\n"
        f"- [SAIU] {old_part_name} (Cód. Item: {old_item_identifier})\n"
        f"- [ENTROU] {new_part_name} (Cód. Item: {new_item_identifier})"
        f"\nNota: {payload.notes or 'N/A'}"
    )
    
    comment_schema = MaintenanceCommentCreate(comment_text=comment_text)
    new_comment = await create_comment(
        db=db,
        comment_in=comment_schema,
        request_id=request_id,
        user_id=user.id,
        organization_id=organization_id
    )
    
    # 7. Flush e Carregar Relações para a RESPOSTA
    await db.flush()
    
    await db.refresh(new_comment, ["user"])
    if new_comment.user:
        await db.refresh(new_comment.user, ["organization"])

    await db.refresh(db_log, ["user"])
    if db_log.user:
        await db.refresh(db_log.user, ["organization"])
        
    await db.refresh(db_log, ["component_removed"])
    if db_log.component_removed:
        await db.refresh(db_log.component_removed, ["part", "inventory_transaction"])
        if db_log.component_removed.part:
            await db.refresh(db_log.component_removed.part, ["items"])
        if db_log.component_removed.inventory_transaction:
            await db.refresh(db_log.component_removed.inventory_transaction, ["item", "user"])
            if db_log.component_removed.inventory_transaction.user:
                 await db.refresh(db_log.component_removed.inventory_transaction.user, ["organization"])

    await db.refresh(db_log, ["component_installed"])
    if db_log.component_installed:
        await db.refresh(db_log.component_installed, ["part", "inventory_transaction"])
        if db_log.component_installed.part:
            await db.refresh(db_log.component_installed.part, ["items"])
        if db_log.component_installed.inventory_transaction:
            await db.refresh(db_log.component_installed.inventory_transaction, ["item", "user"])
            if db_log.component_installed.inventory_transaction.user:
                 await db.refresh(db_log.component_installed.inventory_transaction.user, ["organization"])

    return db_log, new_comment, reported_by_id


# --- NOVA FUNÇÃO: INSTALAÇÃO DIRETA ---
async def perform_new_installation(
    db: AsyncSession, 
    *, 
    request_id: int, 
    payload: InstallComponentPayload, 
    user: User
) -> Tuple[MaintenancePartChange, MaintenanceComment, Optional[int]]: 
    
    # 1. Validar o chamado
    request = await db.get(MaintenanceRequest, request_id)
    if not request or request.organization_id != user.organization_id:
        raise ValueError("Chamado de manutenção não encontrado.")
    if not request.vehicle_id:
        raise ValueError("Chamado não está associado a um veículo.")
        
    vehicle_id = request.vehicle_id
    organization_id = user.organization_id
    reported_by_id = request.reported_by_id 

    # 2. Buscar o Item Novo (Disponível)
    new_item = await crud.crud_part.get_item_by_id(db, item_id=payload.new_item_id, organization_id=organization_id)
    if not new_item:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não encontrado.")
    if new_item.status != InventoryItemStatus.DISPONIVEL:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não está 'Disponível'. Status atual: {new_item.status}")

    # 3. Realizar a Instalação (Mudar status para EM_USO)
    try:
        install_notes = f"Instalação Direta via Chamado #{request_id}"
        if payload.notes:
            install_notes = f"{payload.notes} ({install_notes})"

        updated_item = await crud.part.change_item_status(
            db=db,
            item=new_item,
            new_status=InventoryItemStatus.EM_USO,
            user_id=user.id,
            vehicle_id=vehicle_id,
            notes=install_notes 
        )
    except Exception as e:
        raise e

    # 4. Buscar o Componente recém-criado
    stmt_comp = select(VehicleComponent).join(
        InventoryTransaction, VehicleComponent.inventory_transaction_id == InventoryTransaction.id
    ).where(
        InventoryTransaction.item_id == updated_item.id,
        InventoryTransaction.transaction_type == TransactionType.INSTALACAO
    ).order_by(InventoryTransaction.timestamp.desc()).limit(1)

    res_comp = await db.execute(stmt_comp)
    new_component = res_comp.scalars().first()
    
    if not new_component:
        raise Exception("Falha ao encontrar o registro do componente após a instalação.")

    # 5. Carregar relações para o Log
    await db.refresh(new_component, ["part", "inventory_transaction"])
    if new_component.inventory_transaction:
        await db.refresh(new_component.inventory_transaction, ["item"])

    new_part_name = new_component.part.name
    new_item_identifier = new_component.inventory_transaction.item.item_identifier

    # 6. Criar o Log de Troca (component_removed_id é NULL)
    db_log = MaintenancePartChange(
        maintenance_request_id=request_id,
        user_id=user.id,
        notes=payload.notes,
        component_removed_id=None, # <-- NENHUM REMOVIDO
        component_installed_id=new_component.id
    )
    db.add(db_log)
    
    # 7. Criar Comentário Automático
    comment_text = (
        f"Instalação de novo componente realizada por {user.full_name}:\n"
        f"- [INSTALADO] {new_part_name} (Cód. Item: {new_item_identifier})"
        f"\nNota: {payload.notes or 'N/A'}"
    )
    
    comment_schema = MaintenanceCommentCreate(comment_text=comment_text)
    new_comment = await create_comment(
        db=db,
        comment_in=comment_schema,
        request_id=request_id,
        user_id=user.id,
        organization_id=organization_id
    )
    
    # 8. Flush e Refresh
    await db.flush()
    
    await db.refresh(new_comment, ["user"])
    if new_comment.user:
        await db.refresh(new_comment.user, ["organization"])

    await db.refresh(db_log, ["user", "component_installed"])
    if db_log.user:
        await db.refresh(db_log.user, ["organization"])
    
    if db_log.component_installed:
        await db.refresh(db_log.component_installed, ["part", "inventory_transaction"])
        if db_log.component_installed.part:
            await db.refresh(db_log.component_installed.part, ["items"])
        if db_log.component_installed.inventory_transaction:
            await db.refresh(db_log.component_installed.inventory_transaction, ["item", "user"])
            if db_log.component_installed.inventory_transaction.user:
                 await db.refresh(db_log.component_installed.inventory_transaction.user, ["organization"])

    return db_log, new_comment, reported_by_id


# --- FUNÇÃO "REVERTER" ---
async def revert_part_change(
    db: AsyncSession, *, change_id: int, user: User
) -> Tuple[MaintenancePartChange, MaintenanceComment, Optional[int]]:
    
    # 1. Encontra o log da troca original
    stmt = select(MaintenancePartChange).where(
        MaintenancePartChange.id == change_id
    ).options(
        selectinload(MaintenancePartChange.component_installed).options(
            selectinload(VehicleComponent.part),
            selectinload(VehicleComponent.inventory_transaction).selectinload(InventoryTransaction.item)
        ),
        selectinload(MaintenancePartChange.component_removed).options(
            selectinload(VehicleComponent.part),
            selectinload(VehicleComponent.inventory_transaction).selectinload(InventoryTransaction.item)
        ),
        selectinload(MaintenancePartChange.maintenance_request)
    )
    
    log_entry = (await db.execute(stmt)).scalar_one_or_none()

    if not log_entry:
        raise ValueError("Registro de troca não encontrado.")
        
    if log_entry.maintenance_request.organization_id != user.organization_id:
        raise ValueError("Você não tem permissão para reverter esta troca.")
    if log_entry.is_reverted:
        raise ValueError("Esta troca já foi revertida.")
        
    component_to_revert = log_entry.component_installed
    component_to_reactivate = log_entry.component_removed 
    
    if not component_to_revert:
        raise ValueError("Componente instalado (errado) não encontrado no log.")
    if not component_to_revert.is_active:
        raise ValueError("O componente instalado (errado) já está inativo. Não pode ser revertido.")
        
    vehicle_id = log_entry.maintenance_request.vehicle_id

    # 2. Reverte a instalação (Remove o instalado)
    try:
        revert_notes = f"Reversão da troca #{log_entry.id} (Chamado #{log_entry.maintenance_request_id})"
        await crud.crud_vehicle_component.discard_component(
            db=db,
            component_id=component_to_revert.id,
            user_id=user.id,
            organization_id=user.organization_id,
            final_status=InventoryItemStatus.DISPONIVEL, 
            notes=revert_notes
        )
    except Exception as e:
        raise e 

    # 3. Re-ativa a Peça Antiga (SE EXISTIR - IMPORTANTE PARA INSTALAÇÃO DIRETA)
    part_name_reactivated = "Nenhum"
    item_identifier_reactivated = "N/A"

    if component_to_reactivate:
        if not component_to_reactivate.inventory_transaction or not component_to_reactivate.inventory_transaction.item:
            raise ValueError("Item de inventário do componente original não pode ser determinado.")
            
        item_to_reactivate = component_to_reactivate.inventory_transaction.item

        # Garante que está no estoque para poder instalar
        if item_to_reactivate.status != InventoryItemStatus.DISPONIVEL:
            try:
                await crud.part.change_item_status(
                    db=db,
                    item=item_to_reactivate,
                    new_status=InventoryItemStatus.DISPONIVEL, 
                    user_id=user.id,
                    vehicle_id=None, 
                    notes=f"Retorno ao estoque para reversão da troca #{log_entry.id}"
                )
            except Exception as e:
                 raise ValueError(f"Falha ao re-colocar o item original em estoque: {e}")
        
        # Reinstala
        try:
            reinstall_notes = f"Re-instalação via Reversão da troca #{log_entry.id} (Chamado #{log_entry.maintenance_request_id})"
            await crud.part.change_item_status(
                db=db,
                item=item_to_reactivate, 
                new_status=InventoryItemStatus.EM_USO, 
                user_id=user.id,
                vehicle_id=vehicle_id,
                notes=reinstall_notes
            )
            part_name_reactivated = component_to_reactivate.part.name
            item_identifier_reactivated = component_to_reactivate.inventory_transaction.item.item_identifier
        except Exception as e:
            raise ValueError(f"Falha ao re-instalar o componente original: {e}")


    # 4. Atualiza o log
    log_entry.is_reverted = True
    db.add(log_entry)
    
    # 5. Cria comentário de log
    part_name_reverted = component_to_revert.part.name
    item_identifier_reverted = component_to_revert.inventory_transaction.item.item_identifier
    
    comment_text = (
        f"Troca revertida por {user.full_name}:\n"
        f"- [SAIU] {part_name_reverted} (Cód. Item: {item_identifier_reverted}) - Retornou ao estoque.\n"
    )
    
    if component_to_reactivate:
        comment_text += f"- [ENTROU] {part_name_reactivated} (Cód. Item: {item_identifier_reactivated}) - Re-instalado no veículo."
    else:
        comment_text += "- [INFO] Nenhuma peça anterior foi re-instalada (era uma instalação nova)."

    comment_schema = MaintenanceCommentCreate(comment_text=comment_text)
    new_comment = await create_comment(
        db=db,
        comment_in=comment_schema,
        request_id=log_entry.maintenance_request_id,
        user_id=user.id,
        organization_id=user.organization_id
    )
    
    # 6. Flush e Refresh
    await db.flush()
    await db.refresh(new_comment, ["user"])
    if new_comment.user:
        await db.refresh(new_comment.user, ["organization"])
        
    await db.refresh(log_entry, ["user", "component_removed", "component_installed"])
    
    return log_entry, new_comment, log_entry.maintenance_request.reported_by_id


# --- FUNÇÃO get_request (CORRIGIDA COM CARREGAMENTO PROFUNDO) ---
async def get_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> MaintenanceRequest | None:
    """Busca uma solicitação de manutenção específica, carregando todas as relações."""
    stmt = select(MaintenanceRequest).where(
        MaintenanceRequest.id == request_id, MaintenanceRequest.organization_id == organization_id
    ).options(
        selectinload(MaintenanceRequest.reporter).selectinload(User.organization),
        selectinload(MaintenanceRequest.approver).selectinload(User.organization),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.services), 
        selectinload(MaintenanceRequest.comments).options(
            selectinload(MaintenanceComment.user).selectinload(User.organization)
        ),
        selectinload(MaintenanceRequest.part_changes).options(
            selectinload(MaintenancePartChange.user).selectinload(User.organization),
            selectinload(MaintenancePartChange.component_removed).options(
                selectinload(VehicleComponent.part).options(selectinload(Part.items)),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            ),
            selectinload(MaintenancePartChange.component_installed).options(
                selectinload(VehicleComponent.part).options(selectinload(Part.items)),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# --- FUNÇÃO get_all_requests (CORRIGIDA COM CARREGAMENTO PROFUNDO) ---
async def get_all_requests(
    db: AsyncSession, *, 
    organization_id: int, 
    search: str | None = None, 
    skip: int = 0, 
    limit: int = 100,
    vehicle_id: int | None = None
) -> List[MaintenanceRequest]:
    """Busca todas as solicitações, carregando TODAS as relações necessárias."""
    stmt = select(MaintenanceRequest).where(MaintenanceRequest.organization_id == organization_id)

    if vehicle_id:
        stmt = stmt.where(MaintenanceRequest.vehicle_id == vehicle_id)
    
    if search:
        search_term_text = f"%{search}%"
        search_filters = [
            MaintenanceRequest.problem_description.ilike(search_term_text),
            Vehicle.brand.ilike(search_term_text),
            Vehicle.model.ilike(search_term_text)
        ]
        try:
            search_id = int(search)
            search_filters.append(MaintenanceRequest.id == search_id)
        except ValueError:
            pass 
        stmt = stmt.join(MaintenanceRequest.vehicle).where(or_(*search_filters))

    stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).options(
        selectinload(MaintenanceRequest.reporter).selectinload(User.organization),
        selectinload(MaintenanceRequest.approver).selectinload(User.organization),
        selectinload(MaintenanceRequest.vehicle),
        selectinload(MaintenanceRequest.services),
        selectinload(MaintenanceRequest.comments).options(
             selectinload(MaintenanceComment.user).selectinload(User.organization)
        ),
        selectinload(MaintenanceRequest.part_changes).options(
            selectinload(MaintenancePartChange.user).selectinload(User.organization),
            selectinload(MaintenancePartChange.component_removed).options(
                selectinload(VehicleComponent.part).options(selectinload(Part.items)),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            ),
            selectinload(MaintenancePartChange.component_installed).options(
                selectinload(VehicleComponent.part).options(selectinload(Part.items)),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


# --- FUNÇÃO update_request_status (CORRIGIDA: BUSCA EXPLÍCITA DO VEÍCULO) ---
async def update_request_status(
    db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int
) -> MaintenanceRequest:
    """Atualiza o status de uma solicitação e agenda a próxima manutenção se fornecido."""
    
    request_id = db_obj.id
    org_id = db_obj.organization_id
    
    db_obj.status = update_data.status
    db_obj.manager_notes = update_data.manager_notes
    db_obj.approver_id = manager_id
    
    if update_data.status == MaintenanceStatus.CONCLUIDA:
        vehicle = await db.get(Vehicle, db_obj.vehicle_id)
        
        if vehicle:
            changed = False
            if update_data.next_maintenance_date:
                vehicle.next_maintenance_date = update_data.next_maintenance_date
                changed = True
            
            if update_data.next_maintenance_km is not None:
                vehicle.next_maintenance_km = update_data.next_maintenance_km
                changed = True
            
            if changed:
                db.add(vehicle)

    db.add(db_obj)
    
    await db.commit()
    
    loaded_request = await get_request(db, request_id=request_id, organization_id=org_id)
    if not loaded_request:
        raise Exception("Falha ao recarregar o chamado após a atualização.")
        
    return loaded_request

async def create_comment(
    db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int
) -> MaintenanceComment:
    request_obj = await db.get(MaintenanceRequest, request_id)
    if not request_obj or request_obj.organization_id != organization_id:
        raise ValueError("Solicitação de manutenção não encontrada.")

    db_obj = MaintenanceComment(
        **comment_in.model_dump(),
        request_id=request_id,
        user_id=user_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj, ["user"])
    if db_obj.user:
        await db.refresh(db_obj.user, ["organization"])
    return db_obj

async def get_comments_for_request(
    db: AsyncSession, *, request_id: int, organization_id: int
) -> List[MaintenanceComment]:
    request_obj = await db.get(MaintenanceRequest, request_id)
    if not request_obj or request_obj.organization_id != organization_id:
        return []
    
    stmt = select(MaintenanceComment).where(MaintenanceComment.request_id == request_id).order_by(MaintenanceComment.created_at.asc()).options(selectinload(MaintenanceComment.user).selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().all()

# --- NOVA FUNÇÃO DE CONTAGEM REAL ---
async def count_requests_in_current_month(db: AsyncSession, *, organization_id: int) -> int:
    """Conta quantos chamados de manutenção uma organização criou no mês corrente."""
    today = date.today()
    start_of_month = today.replace(day=1)
    
    # Lógica para encontrar o primeiro dia do próximo mês
    if start_of_month.month == 12:
        start_of_next_month = start_of_month.replace(year=start_of_month.year + 1, month=1)
    else:
        start_of_next_month = start_of_month.replace(month=start_of_month.month + 1)

    stmt = (
        select(func.count(MaintenanceRequest.id))
        .where(
            MaintenanceRequest.organization_id == organization_id,
            MaintenanceRequest.created_at >= start_of_month,
            MaintenanceRequest.created_at < start_of_next_month
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()