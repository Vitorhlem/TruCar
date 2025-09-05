from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.models.vehicle_cost_model import VehicleCost
from app.schemas.vehicle_cost_schema import VehicleCostCreate


async def create_cost(
    db: AsyncSession, *, obj_in: VehicleCostCreate, vehicle_id: int, organization_id: int
) -> VehicleCost:
    """Regista um novo custo para um veículo."""
    db_obj = VehicleCost(
        **obj_in.model_dump(),
        vehicle_id=vehicle_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def get_costs_by_vehicle(
    db: AsyncSession, *, vehicle_id: int, skip: int = 0, limit: int = 100
) -> List[VehicleCost]:
    """Busca a lista de custos para um veículo específico."""
    stmt = (
        select(VehicleCost)
        .where(VehicleCost.vehicle_id == vehicle_id)
        .order_by(VehicleCost.date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()