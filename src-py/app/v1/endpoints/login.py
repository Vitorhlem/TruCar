from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Any

from app import crud, deps
from app.core import auth, email_utils, security
from app.core.config import settings
# Agora Msg existe em token_schema
from app.schemas.token_schema import TokenData, Msg
from app.schemas.user_schema import UserRegister, UserPublic
from app.models.user_model import UserRole
# Import do Celery Task
from app.tasks.email_tasks import send_email_async

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
    """
    user_in.email = user_in.email.lower().strip()

    org = await crud.organization.get_organization_by_name(db, name=user_in.organization_name)
    if org:
        raise HTTPException(status_code=400, detail="Uma organização com este nome já está registada.")
    
    user = await crud.user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Um utilizador com este email já está registado.")

    new_user = await crud.user.create_new_organization_and_user(db=db, user_in=user_in)

    if new_user.email in settings.SUPERUSER_EMAILS:
        print(f"✨ Detectado registro de Superusuário ({new_user.email}). Promovendo a ADMIN...")
        new_user.role = UserRole.ADMIN
        
        if new_user.organization:
            new_user.organization.vehicle_limit = -1
            new_user.organization.driver_limit = -1
            new_user.organization.freight_order_limit = -1
            new_user.organization.maintenance_limit = -1
            db.add(new_user.organization)
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user, attribute_names=["organization"])

    return new_user

@router.post("/token", response_model=TokenData)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login."""
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

@router.post("/password-recovery", response_model=Msg, status_code=status.HTTP_202_ACCEPTED)
async def request_password_recovery(
    *,
    db: AsyncSession = Depends(deps.get_db),
    recovery_in: PasswordRecoveryRequest,
):
    """
    Recuperação de senha com envio Assíncrono (Celery).
    """
    user = await crud.user.get_user_by_email(db, email=recovery_in.email)
    
    if user:
        user_with_token = await crud.user.set_password_reset_token(db=db, user=user)
        
        # 1. Gera o HTML do e-mail
        email_html = email_utils.get_password_reset_template(
            user_name=user.full_name,
            token=user_with_token.reset_password_token
        )
        subject = f"{settings.PROJECT_NAME} - Redefinição de Senha"

        # 2. Envia para a fila do Celery
        send_email_async.delay(
            to_emails=[user.email],
            subject=subject,
            message_html=email_html
        )

    return {"msg": "Se um usuário com este e-mail existir, um link para redefinição de senha será enviado."}

@router.post("/reset-password", response_model=Msg, status_code=status.HTTP_200_OK)
async def reset_password(
    *,
    db: AsyncSession = Depends(deps.get_db),
    reset_in: PasswordResetRequest,
):
    email = security.verify_password_reset_token(token=reset_in.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")
        
    user = await crud.user.get_user_by_email(db, email=email)
    if not user or not user.is_active or user.reset_password_token != reset_in.token:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    if user.reset_password_token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    await crud.user.update_password(db=db, db_user=user, new_password=reset_in.new_password)
    
    user.reset_password_token = None
    user.reset_password_token_expires_at = None
    db.add(user)
    await db.commit()
    
    return {"msg": "Sua senha foi redefinida com sucesso."}