# backend/app/api/v1/endpoints/login.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app import crud
from app.api import deps
from app.models.user_model import UserRole
# A LINHA QUE ESTAVA EM FALTA: Importa as funções de autenticação
from app.core.auth import authenticate_user, create_access_token
# Importa os schemas que usamos
from app.schemas.token_schema import TokenData
from app.schemas.user_schema import UserPublic, UserRegister, UserCreate
from app.schemas.organization_schema import OrganizationCreate

router = APIRouter()

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    register_data: UserRegister
):
    """
    Cria uma nova organização e o seu primeiro utilizador (manager).
    """
    user = await crud.user.get_user_by_email(db, email=register_data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Já existe um utilizador com este email no sistema.",
        )

    org_create_schema = OrganizationCreate(
        name=register_data.organization_name,
        sector=register_data.sector
    )
    # Assumindo que o nome do argumento no seu CRUD de organização é 'obj_in'
    new_organization = await crud.organization.create_organization(db, obj_in=org_create_schema)

    user_create_schema = UserCreate(
        full_name=register_data.full_name,
        email=register_data.email,
        password=register_data.password,
        role=UserRole.MANAGER
    )
    # Assumindo que o nome do argumento no seu CRUD de utilizador é 'user_in'
    new_user = await crud.user.create_user(
        db, user_in=user_create_schema, organization_id=new_organization.id
    )

    await db.refresh(new_user, ["organization"])
    return new_user


@router.post("/token", response_model=TokenData)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Endpoint de login que retorna o token e os dados completos do utilizador.
    """
    # 1. Autentica o utilizador. Esta parte está a funcionar.
    user = await authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Cria o token de acesso. Esta parte está a funcionar.
    access_token = create_access_token(data={"sub": str(user.id)})

    # 3. A CORREÇÃO DEFINITIVA: Construímos os objetos de resposta manualmente
    
    # Cria o objeto Pydantic para o token
    from app.schemas.token_schema import Token
    token_obj = Token(access_token=access_token, token_type="bearer")

    # Cria o objeto Pydantic para os dados públicos do utilizador.
    # Isto força o acesso a user.organization. Se a relação não estiver
    # carregada, o erro aconteceria aqui de forma clara. Mas como corrigimos o CRUD,
    # ela estará carregada.
    user_public_obj = UserPublic.from_orm(user)
    
    # Finalmente, cria e retorna o objeto TokenData completo
    return TokenData(user=user_public_obj, token=token_obj)