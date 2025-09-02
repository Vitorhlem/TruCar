from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserPublic

router = APIRouter()


@router.get("/users/", response_model=List[UserPublic])
async def read_demo_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_super_admin)
):
    """
    Lista todos os utilizadores com o papel DEMO_MANAGER.
    Útil para encontrar contas para ativar.
    """
    # Esta função get_users_by_role precisa existir no seu crud_user.py
    users = await crud.user.get_users_by_role(
        db, role=UserRole.DEMO_MANAGER, skip=skip, limit=limit
    )
    return users


@router.post("/users/{user_id}/activate", response_model=UserPublic)
async def activate_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_super_admin)
):
    """
    Ativa um utilizador, promovendo o seu papel de DEMO_MANAGER para MANAGER.
    """
    # Usamos uma função genérica para buscar o utilizador pelo ID
    user_to_activate = await crud.user.get(db, id=user_id)

    if not user_to_activate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador a ativar não encontrado."
        )
    
    if user_to_activate.role != UserRole.CLIENTE_DEMO:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Este utilizador não é um gestor demo."
        )

    activated_user = await crud.user.activate_user(db, user_to_activate=user_to_activate)

    return activated_user