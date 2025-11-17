from typing import Generator, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from fastapi.concurrency import run_in_threadpool
from datetime import date

from app.core.config import settings
from app.db.session import get_db
from app.models.user_model import User, UserRole
from app import crud

from app.crud.crud_demo_usage import demo_usage as crud_demo_usage_instance

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/token",
    auto_error=True
)



async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await run_in_threadpool(
            jwt.decode, token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await crud.user.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Utilizador inativo")
    return current_user

async def get_current_active_manager(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O utilizador não tem permissões de gestor.",
        )
    return current_user

async def get_current_active_driver(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta ação é restrita a motoristas.",
        )
    return current_user

async def get_current_super_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.email not in settings.SUPERUSER_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação restrita a administradores do sistema."
        )
    return current_user

DEMO_MONTHLY_LIMITS = {
    "reports": 5, "fines": 3, "documents": 10, "freight_orders": 5,
    "maintenance_requests": 5, 
    "fuel_logs": 20,
}
DEMO_TOTAL_LIMITS = {
    "vehicles": 3, "users": 3, "parts": 15, "clients": 5,
    "implements": 2,          
    "vehicle_components": 10, 
}
RESOURCE_TO_CRUD_MAP = {
    "vehicles": crud.vehicle, "users": crud.user,
    "parts": crud.part, "clients": crud.client,
    "implements": crud.implement,          
    "vehicle_components": crud.vehicle_component, 
}

def check_demo_limit(resource_type: str):
    async def dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_manager),
    ):
        if current_user.role != UserRole.CLIENTE_DEMO:
            return
        organization_id = current_user.organization_id
        if resource_type in DEMO_MONTHLY_LIMITS:
            limit = DEMO_MONTHLY_LIMITS[resource_type]
            usage = await crud_demo_usage_instance.get_or_create_usage(
                db, organization_id=organization_id, resource_type=resource_type
            )
            if usage.usage_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Limite mensal de {limit} {resource_type.replace('_', ' ')} atingido para a conta demonstração. Considere migrar para um plano pago.",
                )
        if resource_type in DEMO_TOTAL_LIMITS:
            limit = DEMO_TOTAL_LIMITS[resource_type]
            crud_operation = RESOURCE_TO_CRUD_MAP.get(resource_type)
            if crud_operation:
                current_count = await crud_operation.count_by_org(db, organization_id=organization_id)
                if current_count >= limit:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Limite total de {limit} {resource_type.replace('_', ' ')} atingido para a conta demonstração. Exclua itens ou migre para um plano pago.",
                    )
    return dependency