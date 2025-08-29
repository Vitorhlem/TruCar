# ARQUIVO: backend/app/crud/crud_client.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.models.client_model import Client
from app.schemas.client_schema import ClientCreate, ClientUpdate

class CRUDClient:
    async def create(self, db: AsyncSession, *, obj_in: ClientCreate, organization_id: int) -> Client:
        db_obj = Client(**obj_in.model_dump(), organization_id=organization_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, *, id: int, organization_id: int) -> Client | None:
        stmt = select(Client).where(Client.id == id, Client.organization_id == organization_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi_by_org(self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
        stmt = select(Client).where(Client.organization_id == organization_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, *, db_obj: Client, obj_in: ClientUpdate) -> Client:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: Client) -> Client:
        await db.delete(db_obj)
        await db.commit()
        return db_obj

client = CRUDClient()