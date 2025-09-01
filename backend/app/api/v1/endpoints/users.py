from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
# --- ADICIONADO ---
# Importamos User, UserRole e PlanStatus para as verificações
from app.models.user_model import User, UserRole
from app.models.organization_model import PlanStatus
# --- FIM DA ADIÇÃO ---
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
    # O nome da função no crud foi corrigido para get_multi_by_org para padronização
    users = await crud.user.get_multi_by_org(
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
    """Cria um novo utilizador (motorista) DENTRO da organização do gestor logado."""
    # --- LÓGICA DE RESTRIÇÃO DO PLANO DEMO ADICIONADA ---
    if current_user.organization.plan_status == PlanStatus.DEMO:
        # Contamos quantos motoristas (role='driver') a organização já possui
        driver_count = await crud.user.count_by_org(
            db, organization_id=current_user.organization_id, role=UserRole.DRIVER
        )
        if driver_count >= 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seu Plano Demo permite o cadastro de apenas 2 motoristas. Para adicionar mais, realize o upgrade do seu plano."
            )
    # --- FIM DA LÓGICA DE RESTRIÇÃO ---

    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail fornecido já está registado no sistema.",
        )
    
    # A role é definida aqui, no endpoint. Gestores criam motoristas por padrão.
    new_user = await crud.user.create(
        db=db, user_in=user_in, 
        organization_id=current_user.organization_id,
        role=UserRole.DRIVER
    )
    return new_user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Busca os dados de um único utilizador da organização do gestor.
    """
    user = await crud.user.get(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador não encontrado.",
        )
    return user


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
    user = await crud.user.get(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail="O utilizador não foi encontrado nesta organização.",
        )
    updated_user = await crud.user.update(db=db, db_user=user, user_in=user_in)
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
    
    user_to_delete = await crud.user.get(
        db, user_id=user_id, organization_id=current_user.organization_id
    )
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
    
    deleted_user = await crud.user.remove(db=db, db_user=user_to_delete)
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
