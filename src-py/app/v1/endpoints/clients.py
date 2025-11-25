# ARQUIVO: backend/app/api/v1/endpoints/clients.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.audit_log_schema import AuditLogCreate
from app.crud import crud_audit_log
from app import crud, deps
from app.models.user_model import User
from app.schemas.client_schema import ClientCreate, ClientUpdate, ClientPublic

router = APIRouter()

@router.post("/", response_model=ClientPublic, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(deps.check_demo_limit("clients"))])
async def create_client(
    *,
    db: AsyncSession = Depends(deps.get_db),
    client_in: ClientCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Cria um novo cliente para a organização do gestor logado.
    """
    client = await crud.client.create(
        db=db, obj_in=client_in, organization_id=current_user.organization_id
    )
    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="CREATE", resource_type="Clientes", resource_id=str(client.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"name": client.name, "cnpj": client.cnpj}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")
    return client

@router.get("/", response_model=List[ClientPublic])
async def read_clients(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna uma lista de clientes da organização do usuário.
    """
    clients = await crud.client.get_multi_by_org(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return clients

@router.get("/{client_id}", response_model=ClientPublic)
async def read_client_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    client_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Busca um cliente específico pelo ID.
    """
    client = await crud.client.get(db=db, id=client_id, organization_id=current_user.organization_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    return client

@router.put("/{client_id}", response_model=ClientPublic)
async def update_client(
    *,
    db: AsyncSession = Depends(deps.get_db),
    client_id: int,
    client_in: ClientUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Atualiza um cliente (apenas para gestores).
    """
    db_client = await crud.client.get(db=db, id=client_id, organization_id=current_user.organization_id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    
    updated_client = await crud.client.update(db=db, db_obj=db_client, obj_in=client_in)
    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="UPDATE", resource_type="Clientes", resource_id=str(updated_client.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details=client_in.model_dump(exclude_unset=True)
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")

    return updated_client

@router.delete("/{client_id}", response_model=ClientPublic)
async def delete_client(
    *,
    db: AsyncSession = Depends(deps.get_db),
    client_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Exclui um cliente (apenas para gestores).
    """
    db_client = await crud.client.get(db=db, id=client_id, organization_id=current_user.organization_id)
    if not db_client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
    
    # A exclusão irá apagar em cascata as ordens de frete associadas
    deleted_client = await crud.client.remove(db=db, db_obj=db_client)
    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="DELETE", resource_type="Clientes", resource_id=str(client_id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"deleted_name": db_client.name}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")
    return deleted_client