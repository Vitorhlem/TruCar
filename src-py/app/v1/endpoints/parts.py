from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from app.schemas.audit_log_schema import AuditLogCreate
from app.crud import crud_audit_log
import shutil
from app.models.part_model import Part
from pathlib import Path
from pydantic import BaseModel
import logging
import aiofiles
from sqlalchemy.exc import IntegrityError # <-- Importante para tratar o erro
from app import crud, deps
from app.models.user_model import User
from app.models.part_model import PartCategory, InventoryItemStatus
from app.models.notification_model import NotificationType
from app.schemas.part_schema import (
    PartPublic, PartCreate, PartUpdate, 
    InventoryItemPublic, PartListPublic, InventoryItemDetails,
    InventoryItemPage, InventoryItemRow 
)
from app.schemas.inventory_transaction_schema import TransactionPublic
from app.crud import crud_part 
from app.models.inventory_transaction_model import TransactionType

router = APIRouter()

UPLOAD_DIRECTORY = Path("static/uploads/parts")
UPLOAD_INVOICE_DIRECTORY = Path("static/uploads/invoices")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
UPLOAD_INVOICE_DIRECTORY.mkdir(parents=True, exist_ok=True)

async def save_upload_file(upload_file: UploadFile, directory: Path) -> str:
    if not upload_file:
        return None
    extension = Path(upload_file.filename).suffix if upload_file.filename else ""
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = directory / unique_filename
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while content := await upload_file.read(1024 * 1024):
                await buffer.write(content)
    except Exception as e:
        logging.error(f"Falha ao salvar arquivo: {e}")
        return None
    finally:
        await upload_file.close()
    return f"/{file_path}"

@router.post("/", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(deps.check_demo_limit("parts"))])
async def create_part(
    name: str = Form(...),
    category: str = Form(...), 
    minimum_stock: int = Form(...),
    initial_quantity: int = Form(0), 
    db: AsyncSession = Depends(deps.get_db),
    part_number: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    value: Optional[float] = Form(None),
    serial_number: Optional[str] = Form(None), 
    lifespan_km: Optional[int] = Form(None),
    # --- CORREÇÃO: Adicionados os parâmetros de arquivo ---
    file: Optional[UploadFile] = File(None), 
    invoice_file: Optional[UploadFile] = File(None),
    # -----------------------------------------------------
    current_user: User = Depends(deps.get_current_active_manager)
):
    try:
        category_enum = PartCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Valor de categoria inválido: '{category}'. Valores esperados: {[e.value for e in PartCategory]}"
        )
    part_in = PartCreate(
        name=name, category=category_enum, minimum_stock=minimum_stock,
        initial_quantity=initial_quantity, part_number=part_number, 
        brand=brand, location=location, notes=notes, value=value,
        serial_number=serial_number, lifespan_km=lifespan_km
    )
    
    # --- CORREÇÃO: Lógica de salvamento dos arquivos ---
    photo_url = None
    if file:
        photo_url = await save_upload_file(file, UPLOAD_DIRECTORY)
        
    invoice_url = None
    if invoice_file:
        invoice_url = await save_upload_file(invoice_file, UPLOAD_INVOICE_DIRECTORY)
    # ---------------------------------------------------

    try:
        part_db = await crud_part.create(
            db=db, part_in=part_in, organization_id=current_user.organization_id, 
            user_id=current_user.id, photo_url=photo_url, invoice_url=invoice_url
        )
        part_id_to_return = part_db.id
        
        await db.commit()
        return {"id": part_id_to_return, "message": "Peça criada com sucesso."}
    except ValueError as e:
        await db.rollback() 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError as e:
        await db.rollback()
        logging.warning(f"Erro de integridade ao criar peça: {e}")
        if "unique constraint failed: parts.serial_number" in str(e).lower():
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"O número de série '{serial_number}' já está em uso por outra peça."
            )
    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="CREATE", resource_type="Peças", resource_id=str(Part.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"name": Part.name, "part_number": Part.part_number}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")
        raise HTTPException(status_code=500, detail=f"Erro de integridade no banco: {e}")
    except Exception as e: 
        await db.rollback()
        logging.error(f"Erro ao criar peça: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao criar peça: {e}")
@router.put("/{part_id}") 
async def update_part(
    part_id: int,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    category: str = Form(...), 
    minimum_stock: int = Form(...),
    db: AsyncSession = Depends(deps.get_db),
    part_number: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    value: Optional[float] = Form(None),
    serial_number: Optional[str] = Form(None), 
    lifespan_km: Optional[int] = Form(None),
    condition: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None), 
    invoice_file: Optional[UploadFile] = File(None), 
    current_user: User = Depends(deps.get_current_active_manager)
):
    try:
        category_enum = PartCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Valor de categoria inválido: '{category}'. Valores esperados: {[e.value for e in PartCategory]}"
        )
    db_part = await crud_part.get_simple(db, part_id=part_id, organization_id=current_user.organization_id)
    if not db_part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
    part_in = PartUpdate(
        name=name, category=category_enum, minimum_stock=minimum_stock, part_number=part_number, 
        brand=brand, location=location, notes=notes, value=value,
        serial_number=serial_number, lifespan_km=lifespan_km,
        condition=condition
    )
    photo_url = db_part.photo_url
    if file:
        photo_url = await save_upload_file(file, UPLOAD_DIRECTORY)
    invoice_url = db_part.invoice_url
    if invoice_file:
        invoice_url = await save_upload_file(invoice_file, UPLOAD_INVOICE_DIRECTORY)
    try:
        await crud_part.update(
            db=db, db_obj=db_part, obj_in=part_in, photo_url=photo_url, invoice_url=invoice_url
        )
        await db.commit()
        return {"message": "Peça atualizada com sucesso."}
    except IntegrityError as e:
        await db.rollback()
        logging.warning(f"Erro de integridade ao atualizar peça: {e}")
        if "unique constraint failed: parts.serial_number" in str(e).lower():
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"O número de série '{serial_number}' já está em uso por outra peça."
            )
        raise HTTPException(status_code=500, detail=f"Erro de integridade no banco: {e}")
    except Exception as e: 
        await db.rollback()
        logging.error(f"Erro genérico ao atualizar peça: {e}", exc_info=True) 
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar peça: {e}")
    
@router.get("/", response_model=List[PartListPublic])
async def read_parts(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_manager)
):
    parts = await crud_part.get_multi_by_org(
        db, organization_id=current_user.organization_id, search=search, skip=skip, limit=limit
    )
    return parts

@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Deleta uma peça (template).
    Falha se existirem itens de estoque ou histórico vinculados.
    """
    db_part = await crud_part.get_simple(db, part_id=part_id, organization_id=current_user.organization_id)
    if not db_part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
    
    try:
        await crud_part.remove(db=db, id=part_id, organization_id=current_user.organization_id)
        await db.commit()
    except IntegrityError:
        # --- CORREÇÃO PRINCIPAL DO ERRO 500 ---
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Não é possível excluir esta peça pois ela possui itens no estoque ou histórico de movimentações. Remova os itens individualmente primeiro."
        )
    except Exception as e: 
        await db.rollback()
        logging.error(f"Erro ao deletar peça ID {part_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno ao deletar peça.")

class AddItemsPayload(BaseModel):
    quantity: int
    notes: Optional[str] = None

@router.post("/{part_id}/add-items", status_code=status.HTTP_201_CREATED)
async def add_inventory_items(
    part_id: int,
    payload: AddItemsPayload,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    part = await crud_part.get_simple(db, part_id=part_id, organization_id=current_user.organization_id)
    if not part:
        raise HTTPException(status_code=404, detail="Peça (template) não encontrada.")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero.")
    try:
        await crud_part.create_inventory_items(
            db=db, 
            part_id=part.id,
            organization_id=current_user.organization_id,
            quantity=payload.quantity, 
            user_id=current_user.id, 
            notes=payload.notes
        )
        await db.commit()
    except Exception as e:
        await db.rollback()
        logging.error(f"Erro ao adicionar itens: {e}", exc_info=True) 
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar itens: {e}")
    return {"message": "Itens adicionados com sucesso."}

class SetItemStatusPayload(BaseModel):
    new_status: InventoryItemStatus
    related_vehicle_id: Optional[int] = None
    notes: Optional[str] = None

@router.put("/items/{item_id}/set-status", response_model=InventoryItemPublic)
async def set_inventory_item_status(
    item_id: int,
    payload: SetItemStatusPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    item = await crud_part.get_item_by_id(db, item_id=item_id, organization_id=current_user.organization_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item de inventário não encontrado.")
    new_status = payload.new_status
    current_status = item.status

    if new_status == InventoryItemStatus.EM_USO:
        if current_status != InventoryItemStatus.DISPONIVEL:
            raise HTTPException(status_code=400, detail=f"Item não está 'Disponível' e não pode ser colocado em uso (status atual: {current_status}).")
    
    elif new_status == InventoryItemStatus.FIM_DE_VIDA:
        if current_status not in [InventoryItemStatus.DISPONIVEL, InventoryItemStatus.EM_USO]:
             raise HTTPException(status_code=400, detail=f"Item não pode ser descartado pois seu status é '{current_status}'. Somente itens 'Disponível' ou 'Em Uso' podem ser descartados.")
    
    elif current_status != InventoryItemStatus.DISPONIVEL:
         raise HTTPException(status_code=400, detail=f"Não é possível alterar o status do item pois ele não está 'Disponível' (status atual: {current_status}).")
    try:
        updated_item = await crud_part.change_item_status(
            db=db, item=item, new_status=payload.new_status,
            user_id=current_user.id, vehicle_id=payload.related_vehicle_id, notes=payload.notes
        )
        part = await crud_part.get_part_with_stock(db, part_id=item.part_id, organization_id=current_user.organization_id)
        if part and part.stock < part.minimum_stock:
            message = f"Estoque baixo para a peça '{part.name}'. Quantidade atual: {part.stock}."
            await crud.notification.create_notification(
                db,
                message=message,
                notification_type=NotificationType.LOW_STOCK,
                organization_id=part.organization_id, 
                send_to_managers=True,
                related_entity_type="part",
                related_entity_id=part.id
            )
            
        await db.commit()
        await db.refresh(updated_item, ["part"]) 
        return updated_item
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await db.rollback()
        logging.error(f"Erro ao mudar status do item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao mudar status do item: {e}")

@router.get("/items/{item_id}", response_model=InventoryItemDetails)
async def read_item_details(
    item_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    item = await crud_part.get_item_with_details(
        db, item_id=item_id, organization_id=current_user.organization_id
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item de inventário não encontrado.")
    return item

@router.get("/inventory/items/", response_model=InventoryItemPage)
async def read_all_inventory_items(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
    skip: int = 0,
    limit: int = 20,
    status: Optional[InventoryItemStatus] = None,
    part_id: Optional[int] = None,
    vehicle_id: Optional[int] = None,
    search: Optional[str] = None
):
    result = await crud_part.get_all_items_paginated(
        db=db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        status=status,
        part_id=part_id,
        vehicle_id=vehicle_id,
        search=search
    )
    return result

@router.get("/{part_id}/items", response_model=List[InventoryItemPublic])
async def get_items_for_part(
    part_id: int,
    status: Optional[InventoryItemStatus] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    part = await crud_part.get_simple(db, part_id=part_id, organization_id=current_user.organization_id)
    if not part:
        raise HTTPException(status_code=404, detail="Peça (template) não encontrada.")
    items = await crud_part.get_items_for_part(db, part_id=part_id, status=status)
    return items

@router.get("/{part_id}/history", response_model=List[TransactionPublic])
async def read_part_history(
    part_id: int,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_manager)
):
    part = await crud_part.get_simple(db, part_id=part_id, organization_id=current_user.organization_id)
    if not part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
    history = await crud.inventory_transaction.get_transactions_by_part_id(
        db, part_id=part_id, skip=skip, limit=limit
    )
    return history