from typing import Generator, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError
from fastapi.concurrency import run_in_threadpool # <-- 1. IMPORTE A FERRAMENTA

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user_model import User, UserRole
from app.crud import crud_user

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/token"
)

async def get_db() -> Generator[AsyncSession, Any, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # --- 2. EXECUTE A DECODIFICAÇÃO EM UMA THREAD SEPARADA ---
        payload = await run_in_threadpool(
            jwt.decode, token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = await crud_user.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

async def get_current_active_manager(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if current_user.role != UserRole.MANAGER:
        raise HTTPException(
            status_code=403, detail="O usuário não tem privilégios suficientes"
        )
    return current_user