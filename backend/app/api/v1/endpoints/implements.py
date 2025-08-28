# backend/app/api/v1/endpoints/implements.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.implement_schema import ImplementCreate, ImplementUpdate, ImplementPublic

router = APIRouter()

@router.post("/", response_model=ImplementPublic, status_code=status.HTTP_201_CREATED)
async def create_implement(
    *,
    db: AsyncSession = Depends(deps.get_db),
    implement_in: ImplementCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Cria um novo implemento para a organização do gestor logado.
    """
    implement = await crud.implement.create_implement(
        db=db, obj_in=implement_in, organization_id=current_user.organization_id
    )
    return implement

@router.get("/management-list", response_model=List[ImplementPublic])
async def read_all_implements_for_management(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna uma lista de TODOS os implementos da organização,
    sem filtrar por status. Para uso em telas de gerenciamento.
    """
    implements = await crud.implement.get_all_by_org_unfiltered(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return implements

@router.get("/", response_model=List[ImplementPublic])
async def read_implements(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna uma lista de implementos da organização do usuário.
    """
    implements = await crud.implement.get_all_by_org(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return implements

@router.get("/{implement_id}", response_model=ImplementPublic)
async def read_implement_by_id(
    implement_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Busca um único implemento pelo ID."""
    implement = await crud.implement.get_implement(
        db, implement_id=implement_id, organization_id=current_user.organization_id
    )
    if not implement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Implemento não encontrado.")
    return implement

@router.put("/{implement_id}", response_model=ImplementPublic)
async def update_implement(
    *,
    db: AsyncSession = Depends(deps.get_db),
    implement_id: int,
    implement_in: ImplementUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza um implemento (apenas para gestores)."""
    db_implement = await crud.implement.get_implement(
        db, implement_id=implement_id, organization_id=current_user.organization_id
    )
    if not db_implement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Implemento não encontrado.")
    
    updated_implement = await crud.implement.update_implement(db=db, db_obj=db_implement, obj_in=implement_in)
    return updated_implement

@router.delete("/{implement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_implement(
    *,
    db: AsyncSession = Depends(deps.get_db),
    implement_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Exclui um implemento (apenas para gestores)."""
    db_implement = await crud.implement.get_implement(
        db, implement_id=implement_id, organization_id=current_user.organization_id
    )
    if not db_implement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Implemento não encontrado.")
    
    await crud.implement.remove_implement(db=db, db_obj=db_implement)
    return Response(status_code=status.HTTP_204_NO_CONTENT)