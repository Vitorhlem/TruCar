from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app import crud
from app.api import deps
from app.core import auth
from app.schemas.token_schema import TokenData
from app.schemas.user_schema import UserRegister, UserPublic, UserCreate
from app.schemas.organization_schema import OrganizationCreate
from app.models.user_model import UserRole, User

router = APIRouter()

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserRegister
) -> Any:
    # ... (sua função de registo, que já está correta)
    org = await crud.organization.get_organization_by_name(db, name=user_in.organization_name)
    if org:
        raise HTTPException(status_code=400, detail="Uma organização com este nome já está registada.")
    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Um utilizador com este email já está registado.")

    org_to_create = OrganizationCreate(name=user_in.organization_name, sector=user_in.sector)
    new_org = await crud.organization.create_organization(db, obj_in=org_to_create)
    
    user_to_create = UserCreate(
        full_name=user_in.full_name,
        email=user_in.email,
        password=user_in.password,
        role=UserRole.MANAGER
    )
    
    new_user = await crud.user.create_user(
        db, user_in=user_to_create, organization_id=new_org.id
    )
    return new_user


@router.post("/token", response_model=TokenData)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token and user data."""
    user = await auth.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Utilizador inativo")
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})

    # Retorna o dicionário que corresponde exatamente ao schema TokenData
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user 
    }