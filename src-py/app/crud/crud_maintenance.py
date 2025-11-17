from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, cast, Integer
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from datetime import datetime, timezone

from app.models.vehicle_component_model import VehicleComponent
from app.models.maintenance_model import (
    MaintenanceRequest, 
    MaintenanceComment, 
    MaintenancePartChange
)
from app.models.vehicle_model import Vehicle
from app.models.inventory_transaction_model import InventoryTransaction, TransactionType
from app.models.user_model import User
from app.models.part_model import Part, InventoryItem, InventoryItemStatus
from app.schemas.maintenance_schema import (
    MaintenanceRequestCreate, MaintenanceRequestUpdate, MaintenanceCommentCreate,
    ReplaceComponentPayload, 
    ReplaceComponentResponse
)
from app import crud


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


async def perform_component_replacement(
    db: AsyncSession, 
    *, 
    request_id: int, 
    payload: ReplaceComponentPayload, 
    user: User
) -> Tuple[MaintenancePartChange, MaintenanceComment, Optional[int]]: 
    
    request = await db.get(MaintenanceRequest, request_id)
    if not request or request.organization_id != user.organization_id:
        raise ValueError("Chamado de manutenção não encontrado.")
    if not request.vehicle_id:
        raise ValueError("Chamado não está associado a um veículo.")
        
    vehicle_id = request.vehicle_id
    organization_id = user.organization_id
    reported_by_id = request.reported_by_id 

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

    new_item = await crud.crud_part.get_item_by_id(db, item_id=payload.new_item_id, organization_id=organization_id)
    if not new_item:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não encontrado.")
    if new_item.status != InventoryItemStatus.DISPONIVEL:
        raise ValueError(f"Item novo (ID: {payload.new_item_id}) não está 'Disponível'. Status atual: {new_item.status}")

    try:
        install_notes = f"Instalado via Chamado #{request_id}"
        if payload.notes:
            install_notes = f"{payload.notes} ({install_notes})"

        updated_item = await crud.crud_part.change_item_status(
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

    db_log = MaintenancePartChange(
        maintenance_request_id=request_id,
        user_id=user.id,
        notes=payload.notes,
        component_removed_id=uninstalled_component.id,
        component_installed_id=new_component.id
    )
    db.add(db_log)
    
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


async def revert_part_change(
    db: AsyncSession, *, change_id: int, user: User
) -> Tuple[MaintenancePartChange, MaintenanceComment, Optional[int]]:
    """
    Reverte uma troca de peça:
    1. Desinstala o 'component_installed' (Peça B), devolvendo o item ao estoque.
    2. Re-instala o 'component_removed' (Peça A), colocando o item em uso.
    Retorna (log_da_troca_atualizado, comentario_de_reversao, id_do_reporte)
    """
    
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
        
    component_to_revert = log_entry.component_installed # Peça B (a errada)
    component_to_reactivate = log_entry.component_removed # Peça A (a "antiga antiga")
    
    if not component_to_revert:
        raise ValueError("Componente instalado (errado) não encontrado no log.")
    if not component_to_revert.is_active:
        raise ValueError("O componente instalado (errado) já está inativo. Não pode ser revertido.")
        
    if not component_to_reactivate:
        raise ValueError("Componente original (removido) não encontrado no log. Não é possível re-instalar.")
    if not component_to_reactivate.inventory_transaction or not component_to_reactivate.inventory_transaction.item:
        raise ValueError("Item de inventário do componente original não pode ser determinado.")
        
    item_to_reactivate = component_to_reactivate.inventory_transaction.item
    vehicle_id = log_entry.maintenance_request.vehicle_id
    if not vehicle_id:
         raise ValueError("Chamado não está associado a um veículo.")


    try:
        revert_notes = f"Reversão da troca #{log_entry.id} (Chamado #{log_entry.maintenance_request_id})"
        
        await crud.crud_vehicle_component.discard_component(
            db=db,
            component_id=component_to_revert.id,
            user_id=user.id,
            organization_id=user.organization_id,
            final_status=InventoryItemStatus.DISPONIVEL, # Devolve ao estoque
            notes=revert_notes
        )
    except Exception as e:
        raise e 

    
    if item_to_reactivate.status != InventoryItemStatus.DISPONIVEL:
        try:
            await crud.crud_part.change_item_status(
                db=db,
                item=item_to_reactivate,
                new_status=InventoryItemStatus.DISPONIVEL, # Mover para 'Disponível'
                user_id=user.id,
                vehicle_id=None, # Ainda não está no veículo
                notes=f"Retorno ao estoque para reversão da troca #{log_entry.id}"
            )
        except Exception as e:
             raise ValueError(f"Falha ao re-colocar o item original em estoque: {e}")

    try:
        reinstall_notes = f"Re-instalação via Reversão da troca #{log_entry.id} (Chamado #{log_entry.maintenance_request_id})"
        
        await crud.crud_part.change_item_status(
            db=db,
            item=item_to_reactivate, # O item de "Peça A"
            new_status=InventoryItemStatus.EM_USO, # Coloca em uso
            user_id=user.id,
            vehicle_id=vehicle_id, # No mesmo veículo
            notes=reinstall_notes
        )
    except Exception as e:
        raise ValueError(f"Falha ao re-instalar o componente original: {e}")


    log_entry.is_reverted = True
    db.add(log_entry)
    
    part_name_reverted = component_to_revert.part.name
    item_identifier_reverted = component_to_revert.inventory_transaction.item.item_identifier
    
    part_name_reactivated = component_to_reactivate.part.name
    item_identifier_reactivated = component_to_reactivate.inventory_transaction.item.item_identifier
    
    comment_text = (
        f"Troca revertida por {user.full_name}:\n"
        f"- [SAIU] {part_name_reverted} (Cód. Item: {item_identifier_reverted}) - Retornou ao estoque.\n"
        f"- [ENTROU] {part_name_reactivated} (Cód. Item: {item_identifier_reactivated}) - Re-instalado no veículo."
    )
    
    comment_schema = MaintenanceCommentCreate(comment_text=comment_text)
    new_comment = await create_comment(
        db=db,
        comment_in=comment_schema,
        request_id=log_entry.maintenance_request_id,
        user_id=user.id,
        organization_id=user.organization_id
    )
    
    await db.flush()
    await db.refresh(new_comment, ["user"])
    if new_comment.user:
        await db.refresh(new_comment.user, ["organization"])
        
    await db.refresh(log_entry, ["user", "component_removed", "component_installed"])
    
    
    return log_entry, new_comment, log_entry.maintenance_request.reported_by_id

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
        
        selectinload(MaintenanceRequest.comments).options(
            selectinload(MaintenanceComment.user).selectinload(User.organization)
        ),

        selectinload(MaintenanceRequest.part_changes).options(
            selectinload(MaintenancePartChange.user).selectinload(User.organization),
            
            selectinload(MaintenancePartChange.component_removed).options(
                selectinload(VehicleComponent.part).options(
                    selectinload(Part.items) 
                ),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            ),
            
            selectinload(MaintenancePartChange.component_installed).options(
                selectinload(VehicleComponent.part).options( 
                    selectinload(Part.items) 
                ),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_requests(
    db: AsyncSession, *, 
    organization_id: int, 
    search: str | None = None, 
    skip: int = 0, 
    limit: int = 100,
    vehicle_id: int | None = None  # <-- 1. ADICIONE ESTE PARÂMETRO
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

        stmt = stmt.join(MaintenanceRequest.vehicle).where(
            or_(*search_filters)
        )

    stmt = stmt.order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit).options(
        selectinload(MaintenanceRequest.reporter).selectinload(User.organization),
        selectinload(MaintenanceRequest.approver).selectinload(User.organization),
        selectinload(MaintenanceRequest.vehicle),
        
        selectinload(MaintenanceRequest.comments).options(
             selectinload(MaintenanceComment.user).selectinload(User.organization)
        ),
        
        selectinload(MaintenanceRequest.part_changes).options(
            selectinload(MaintenancePartChange.user).selectinload(User.organization),
            
            selectinload(MaintenancePartChange.component_removed).options(
                selectinload(VehicleComponent.part).options(
                    selectinload(Part.items) 
                ),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            ),
            
            selectinload(MaintenancePartChange.component_installed).options(
                selectinload(VehicleComponent.part).options(
                    selectinload(Part.items) 
                ),
                selectinload(VehicleComponent.inventory_transaction).options(
                    selectinload(InventoryTransaction.item),
                    selectinload(InventoryTransaction.user).selectinload(User.organization)
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_request_status(
    db: AsyncSession, *, db_obj: MaintenanceRequest, update_data: MaintenanceRequestUpdate, manager_id: int
) -> MaintenanceRequest:
    """Atualiza o status de uma solicitação e retorna o objeto completo."""
    
    request_id = db_obj.id
    org_id = db_obj.organization_id
    
    db_obj.status = update_data.status
    db_obj.manager_notes = update_data.manager_notes
    db_obj.approver_id = manager_id
    db.add(db_obj)
    
    await db.commit()
    
    loaded_request = await get_request(db, request_id=request_id, organization_id=org_id)
    if not loaded_request:
        raise Exception("Falha ao recarregar o chamado após a atualização.")
        
    return loaded_request

async def create_comment(
    db: AsyncSession, *, comment_in: MaintenanceCommentCreate, request_id: int, user_id: int, organization_id: int
) -> MaintenanceComment:
    """Cria um novo comentário, garantindo que a solicitação pertence à organização."""
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
    """Busca os comentários de uma solicitação, garantindo que a solicitação pertence à organização."""
    request_obj = await db.get(MaintenanceRequest, request_id)
    if not request_obj or request_obj.organization_id != organization_id:
        return []
    
    stmt = select(MaintenanceComment).where(MaintenanceComment.request_id == request_id).order_by(MaintenanceComment.created_at.asc()).options(selectinload(MaintenanceComment.user).selectinload(User.organization))
    result = await db.execute(stmt)
    return result.scalars().all()