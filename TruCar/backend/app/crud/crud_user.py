from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate

async def delete_user(db: AsyncSession, *, db_user: User) -> User:
    """Deleta um usuário do banco de dados."""
    await db.delete(db_user)
    await db.commit()
    return db_user

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

# --- NOVA FUNÇÃO ---
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Retorna uma lista de usuários com paginação."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = await run_in_threadpool(get_password_hash, user_in.password)
    db_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- NOVA FUNÇÃO ---
async def update_user(db: AsyncSession, *, db_user: User, user_in: UserUpdate) -> User:
    """Atualiza os dados de um usuário."""
    update_data = user_in.model_dump(exclude_unset=True)

    # Se uma nova senha foi fornecida, hasheia antes de salvar
    if "password" in update_data and update_data["password"]:
        hashed_password = await run_in_threadpool(get_password_hash, update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    
    is_correct_password = await run_in_threadpool(verify_password, password, user.hashed_password)
    if not is_correct_password:
        return None
        
    return user