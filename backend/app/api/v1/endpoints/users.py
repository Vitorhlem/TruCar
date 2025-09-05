from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.schemas.user_schema import UserCreate, UserUpdate, UserPublic, UserStats, UserPasswordUpdate, UserNotificationPrefsUpdate
from app.core.security import verify_password
from app.api import deps
from app.models.user_model import User, UserRole

router = APIRouter()


@router.get("/", response_model=List[UserPublic])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Lista todos os utilizadores da organização do gestor."""
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
    if current_user.role == UserRole.CLIENTE_DEMO:
        driver_count = await crud.user.count_by_org(
            db, organization_id=current_user.organization_id, role=UserRole.DRIVER
        )
        if driver_count >= 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A sua conta de demonstração permite o cadastro de apenas 2 motoristas."
            )

    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O e-mail fornecido já está registado no sistema.",
        )
    
    new_user = await crud.user.create(
        db=db, user_in=user_in, 
        organization_id=current_user.organization_id,
        role=user_in.role or UserRole.DRIVER
    )
    return new_user

@router.put("/me/password", response_model=UserPublic)
async def update_current_user_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password_data: UserPasswordUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Atualiza a senha do utilizador logado."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha atual está incorreta."
        )
    
    updated_user = await crud.user.update_password(
        db, db_user=current_user, new_password=password_data.new_password
    )
    return updated_user

# --- NOVO ENDPOINT ADICIONADO ---
@router.put("/me/preferences", response_model=UserPublic)
async def update_current_user_preferences(
    *,
    db: AsyncSession = Depends(deps.get_db),
    prefs_in: UserNotificationPrefsUpdate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Atualiza as preferências de notificação do utilizador logado.
    """
    update_data = UserUpdate(**prefs_in.model_dump())
    updated_user = await crud.user.update(db=db, db_user=current_user, user_in=update_data)
    return updated_user
# --- FIM DA ADIÇÃO ---

@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Busca os dados de um único utilizador da organização do gestor."""
    user = await crud.user.get(
        db, id=user_id, organization_id=current_user.organization_id
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
    user_to_update = await crud.user.get(
        db, id=user_id, organization_id=current_user.organization_id
    )
    if not user_to_update:
        raise HTTPException(
            status_code=404,
            detail="O utilizador não foi encontrado nesta organização.",
        )

    if user_in.role is not None and user_in.role != user_to_update.role:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores do sistema podem alterar o papel de um utilizador."
            )
    
    updated_user = await crud.user.update(db=db, db_user=user_to_update, user_in=user_in)
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
        db, id=user_id, organization_id=current_user.organization_id
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