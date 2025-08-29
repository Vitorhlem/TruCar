# ARQUIVO: backend/app/crud/crud_freight_order.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.freight_order_model import FreightOrder
from app.models.stop_point_model import StopPoint
from app.schemas.freight_order_schema import FreightOrderCreate, FreightOrderUpdate

class CRUDFreightOrder:
    async def create_with_stops(self, db: AsyncSession, *, obj_in: FreightOrderCreate, organization_id: int) -> FreightOrder:
        # Cria a Ordem de Frete principal
        freight_order_data = obj_in.model_dump(exclude={"stop_points"})
        db_freight_order = FreightOrder(**freight_order_data, organization_id=organization_id)
        
        # Cria os Pontos de Parada e os associa à Ordem de Frete
        for stop_point_data in obj_in.stop_points:
            db_stop_point = StopPoint(**stop_point_data.model_dump())
            db_freight_order.stop_points.append(db_stop_point)
            
        db.add(db_freight_order)
        await db.commit()
        await db.refresh(db_freight_order)
        return db_freight_order

    async def get(self, db: AsyncSession, *, id: int, organization_id: int) -> FreightOrder | None:
        stmt = (
            select(FreightOrder)
            .where(FreightOrder.id == id, FreightOrder.organization_id == organization_id)
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.vehicle),
                selectinload(FreightOrder.driver),
                selectinload(FreightOrder.stop_points) # Carregamento otimizado
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_multi_by_org(self, db: AsyncSession, *, organization_id: int, skip: int = 0, limit: int = 100) -> List[FreightOrder]:
        stmt = (
            select(FreightOrder)
            .where(FreightOrder.organization_id == organization_id)
            .options(
                selectinload(FreightOrder.client),
                selectinload(FreightOrder.vehicle),
                selectinload(FreightOrder.driver)
            )
            .order_by(FreightOrder.id.desc())
            .offset(skip).limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(self, db: AsyncSession, *, db_obj: FreightOrder, obj_in: FreightOrderUpdate) -> FreightOrder:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

freight_order = CRUDFreightOrder()