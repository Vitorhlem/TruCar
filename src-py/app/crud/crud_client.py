from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.crud.crud_vehicle import count_by_org
from app.models.client_model import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate


async def create(db: AsyncSession, *, obj_in: ClientCreate, organization_id: int) -> Client:
    db_obj = Client(**obj_in.model_dump(), organization_id=organization_id)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get(db: AsyncSession, *, id: int, organization_id: Optional[int] = None) -> Optional[Client]:
    """
    Obtém um cliente por ID, opcionalmente filtrando pela organização.
    """
    stmt = select(Client).where(Client.id == id)
    if organization_id:
        stmt = stmt.where(Client.organization_id == organization_id)

    result = await db.execute(stmt)
    return result.scalars().first()

async def get_multi_by_org(db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
    stmt = select(Client).where(Client.organization_id == organization_id).order_by(Client.name).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update(db: AsyncSession, *, db_obj: Client, obj_in: ClientUpdate) -> Client:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def remove(db: AsyncSession, *, db_obj: Client) -> Client:
    await db.delete(db_obj)
    await db.commit()
    return db_obj

async def count(db: AsyncSession, *, organization_id: int) -> int:
    """Implementa o método 'count' genérico para uso em APIs como demo-stats."""
    return await count_by_org(db, organization_id=organization_id)