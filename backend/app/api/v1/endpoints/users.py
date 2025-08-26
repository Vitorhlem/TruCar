from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserPublic, UserStats

router = APIRouter()

@router.get("/", response_model=List[UserPublic])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Lista todos os utilizadores da organização do gestor."""
    users = await crud.user.get_users(
        db, organization_id=current_user.organization_id, skip=skip, limit=limit
    )
    return users

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Cria um novo utilizador DENTRO da organização do gestor logado."""
    user = await crud.user.get_user_by_email(db, email=user_in.email)
    # A verificação de e-mail duplicado deve ser global para evitar conflitos de login
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail fornecido já está registado no sistema.",
        )
    
    new_user = await crud.user.create_user(
        db=db, user_in=user_in, 
        organization_id=current_user.organization_id
    )
    return new_user



@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna os dados do utilizador logado."""
    return current_user

@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Atualiza um utilizador da organização do gestor."""
    user = await crud.user.get_user(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="O utilizador não foi encontrado nesta organização.",
        )
    updated_user = await crud.user.update_user(db=db, db_user=user, user_in=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=UserPublic)
async def delete_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Exclui um utilizador da organização do gestor."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode excluir a sua própria conta de gestor.",
        )
    
    user_to_delete = await crud.user.get_user(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
    
    deleted_user = await crud.user.delete_user(db=db, db_user=user_to_delete)
    return deleted_user

@router.get("/{user_id}/stats", response_model=UserStats)
async def read_user_stats(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Retorna as estatísticas de um utilizador específico da organização do gestor."""
    stats = await crud.user.get_user_stats(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not stats:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado para gerar estatísticas.")
    return stats