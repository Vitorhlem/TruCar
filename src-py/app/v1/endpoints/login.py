from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Any

from app import crud, deps
from app.core import auth, email_utils, security
# --- ADIÇÃO: Importar settings para verificar SUPERUSER_EMAILS ---
from app.core.config import settings
# -----------------------------------------------------------------
from app.schemas.token_schema import TokenData
from app.schemas.user_schema import UserRegister, UserPublic, UserCreate
from app.schemas.organization_schema import OrganizationCreate
from app.models.user_model import User, UserRole

router = APIRouter()

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserRegister
) -> Any:
    """
    Regista um novo utilizador. 
    Se for admin@admin.com, cria como ADMIN ilimitado.
    Caso contrário, cria como CLIENTE_DEMO.
    """
    # 1. Normalizar e-mail
    user_in.email = user_in.email.lower().strip()

    # Validações
    org = await crud.organization.get_organization_by_name(db, name=user_in.organization_name)
    if org:
        raise HTTPException(status_code=400, detail="Uma organização com este nome já está registada.")
    
    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Um utilizador com este email já está registado.")

    # 2. Cria o utilizador (Padrão: Demo)
    new_user = await crud.user.create_new_organization_and_user(db=db, user_in=user_in)

    # 3. VERIFICAÇÃO DE ADMIN (Auto-Promoção)
    if new_user.email in settings.SUPERUSER_EMAILS:
        print(f"✨ Detectado registro de Superusuário ({new_user.email}). Promovendo a ADMIN...")
        
        # Define explicitamente como ADMIN
        new_user.role = UserRole.ADMIN 
        
        # Remove limites da organização
        if new_user.organization:
            new_user.organization.vehicle_limit = -1
            new_user.organization.driver_limit = -1
            new_user.organization.freight_order_limit = -1
            new_user.organization.maintenance_limit = -1
            db.add(new_user.organization)
        
        db.add(new_user)
        await db.commit()
        
        # --- CORREÇÃO DO ERRO 500 ---
        # Recarrega o usuário E a organização para o Pydantic não falhar
        await db.refresh(new_user, attribute_names=["organization"]) 
        # ----------------------------

    return new_user

@router.post("/token", response_model=TokenData)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token and user data."""
    # Normalizar email no login também
    email_input = form_data.username.lower().strip()
    
    user = await auth.authenticate_user(
        db, email=email_input, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Utilizador inativo")
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user 
    }

@router.post("/password-recovery", status_code=status.HTTP_202_ACCEPTED)
async def request_password_recovery(
    *,
    db: AsyncSession = Depends(deps.get_db),
    recovery_in: PasswordRecoveryRequest,
):
    user = await crud.user.get_user_by_email(db, email=recovery_in.email)
    
    if user:
        user_with_token = await crud.user.set_password_reset_token(db=db, user=user)
        email_utils.send_password_reset_email(
            to_email=user.email,
            user_name=user.full_name,
            token=user_with_token.reset_password_token
        )

    return {"msg": "Se um usuário com este e-mail existir, um link para redefinição de senha será enviado."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    reset_in: PasswordResetRequest,
):
    email = security.verify_password_reset_token(token=reset_in.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O token de redefinição de senha é inválido ou expirou.",
        )
        
    user = await crud.user.get_user_by_email(db, email=email)
    if not user or not user.is_active or user.reset_password_token != reset_in.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O token de redefinição de senha é inválido ou expirou.",
        )

    if user.reset_password_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O token de redefinição de senha é inválido ou expirou.",
        )

    await crud.user.update_password(db=db, db_user=user, new_password=reset_in.new_password)
    
    user.reset_password_token = None
    user.reset_password_token_expires_at = None
    db.add(user)
    await db.commit()
    
    return {"msg": "Sua senha foi redefinida com sucesso."}