from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app import crud
from app.api import deps
from app.core import auth 
from app.models.user_model import User, UserRole
from app.schemas.user_schema import UserPublic
from app.schemas.organization_schema import OrganizationPublic, OrganizationUpdate
from app.schemas.token_schema import Token 

router = APIRouter()


# --- ROTAS DE GESTÃO DE ORGANIZAÇÕES ---

@router.get("/organizations/", response_model=List[OrganizationPublic])
async def read_organizations_as_admin(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None, # Parâmetro de filtro: 'demo' ou 'active'
    current_user: User = Depends(deps.get_current_super_admin)
):
    """(Super Admin) Lista todas as organizações, com opção de filtro por status."""
    organizations = await crud.organization.get_multi(
        db, skip=skip, limit=limit, status=status
    )
    return organizations


@router.put("/organizations/{org_id}", response_model=OrganizationPublic)
async def update_organization_as_admin(
    *,
    db: AsyncSession = Depends(deps.get_db),
    org_id: int,
    org_in: OrganizationUpdate,
    current_user: User = Depends(deps.get_current_super_admin)
):
    """(Super Admin) Atualiza os dados de uma organização (ex: nome, setor)."""
    org_to_update = await crud.organization.get(db=db, id=org_id)
    if not org_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organização não encontrada."
        )
    
    updated_org = await crud.organization.update(db=db, db_obj=org_to_update, obj_in=org_in)
    return updated_org


# --- ROTAS DE GESTÃO DE UTILIZADORES (ATIVAÇÃO) ---

@router.get("/users/demo", response_model=List[UserPublic])
async def read_demo_users_as_admin(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin)
):
    """(Super Admin) Retorna a lista de todos os utilizadores com o papel CLIENTE_DEMO."""
    demo_users = await crud.user.get_users_by_role(
        db, role=UserRole.CLIENTE_DEMO
    )
    return demo_users

@router.get("/users/all", response_model=List[UserPublic])
async def read_all_users_as_admin(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_super_admin)
):
    """(Super Admin) Retorna a lista de TODOS os utilizadores da plataforma."""
    all_users = await crud.user.get_multi_by_org(db)
    return all_users


@router.post("/users/{user_id}/activate", response_model=UserPublic)
async def activate_user_account_as_admin(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_super_admin)
):
    """(Super Admin) Ativa um utilizador, promovendo o seu papel para CLIENTE_ATIVO."""
    user_to_activate = await crud.user.get(db=db, id=user_id)

    if not user_to_activate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador a ser ativado não foi encontrado."
        )
    
    if user_to_activate.role != UserRole.CLIENTE_DEMO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este utilizador não é um cliente demo."
        )

    activated_user = await crud.user.activate_user(db=db, user_to_activate=user_to_activate)
    return activated_user


# --- ROTA DE LOGIN SOMBRA ADICIONADA ---
@router.post("/users/{user_id}/impersonate", response_model=Token)
async def impersonate_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_super_admin) # Protegido
):
    """
    (Super Admin) Gera um token de acesso para entrar como outro utilizador.
    """
    user_to_impersonate = await crud.user.get(db=db, id=user_id)

    if not user_to_impersonate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador alvo não encontrado."
        )

    # Regra de segurança: impede que um super admin personifique outro.
    if user_to_impersonate.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Não é permitido personificar outro super administrador."
        )

    # Geramos o token para o utilizador-alvo
    access_token = auth.create_access_token(
        data={"sub": str(user_to_impersonate.id)}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
