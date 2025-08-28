# backend/app/crud/crud_implement.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.implement_model import Implement
from app.schemas.implement_schema import ImplementCreate, ImplementUpdate

async def create_implement(
    db: AsyncSession, *, obj_in: ImplementCreate, organization_id: int
) -> Implement:
    """Cria um novo implemento associado a uma organização."""
    db_obj = Implement(
        **obj_in.model_dump(), 
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_implement(
    db: AsyncSession, *, implement_id: int, organization_id: int
) -> Implement | None:
    """Busca um implemento específico pelo ID, garantindo que pertence à organização correta."""
    stmt = select(Implement).where(
        Implement.id == implement_id, 
        Implement.organization_id == organization_id
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_all_by_org(
    db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100
) -> List[Implement]:
    """Retorna uma lista de todos os implementos de uma organização específica."""
    stmt = (
        select(Implement)
        .where(Implement.organization_id == organization_id)
        .order_by(Implement.name)
        .offset(skip).limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_implement(
    db: AsyncSession, *, db_obj: Implement, obj_in: ImplementUpdate
) -> Implement:
    """Atualiza os dados de um implemento."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove_implement(db: AsyncSession, *, db_obj: Implement) -> Implement:
    """Remove um implemento do banco de dados."""
    await db.delete(db_obj)
    await db.commit()
    return db_obj