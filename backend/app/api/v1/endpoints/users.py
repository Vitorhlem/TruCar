from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from app import crud, models
from app.api import deps
from app.models import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserPublic, UserStats

router = APIRouter()

@router.get("/", response_model=List[UserPublic])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.user_model.User = Depends(deps.get_current_active_manager),
):
     users = await crud.user.get_users(db, organization_id=current_user.organization_id, skip=skip, limit=limit)
     return users

@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: models.user_model.User = Depends(deps.get_current_active_manager),
):
    """Cria um novo utilizador DENTRO da organização do gestor logado."""
    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail fornecido já está registado no sistema.",
        )
    # Passa o organization_id do gestor logado para a função de criação
    new_user = await crud.user.create_user(
        db=db, user_in=user_in, organization_id=current_user.organization_id
    )
    return new_user


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: models.user_model.User = Depends(deps.get_current_active_user),
):
    return current_user

@router.put("/{user_id}", response_model=UserPublic)
async def update_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: models.user_model.User = Depends(deps.get_current_active_manager),
):
    user = await crud.user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="O usuário com este ID não foi encontrado no sistema.",
        )
    updated_user = await crud.user.update_user(db=db, db_user=user, user_in=user_in)
    return updated_user

@router.delete("/{user_id}", response_model=UserPublic)
async def delete_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: models.user_model.User = Depends(deps.get_current_active_manager),
):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode deletar sua própria conta de gestor.",
        )
    user_to_delete = await crud.user.get_user(db, user_id=user_id)
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    try:
        deleted_user = await crud.user.delete_user(db=db, db_user=user_to_delete)
        return deleted_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um usuário que já possui viagens registradas.",
        )

@router.get("/{user_id}/stats", response_model=UserStats)
async def read_user_stats(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Retorna as estatísticas de um usuário específico. Acessível apenas para gestores.
    """
    stats = await crud.user.get_user_stats(db, user_id=user_id)
    return stats