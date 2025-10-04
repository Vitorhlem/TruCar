from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # Garanta que está importado
from typing import List, Optional
from datetime import date

from app.models.vehicle_cost_model import VehicleCost
from app.schemas.vehicle_cost_schema import VehicleCostCreate


async def create_cost(
    db: AsyncSession, *, obj_in: VehicleCostCreate, vehicle_id: int, organization_id: int, commit: bool = True
) -> VehicleCost:
    """Regista um novo custo para um veículo."""
    db_obj = VehicleCost(
        **obj_in.model_dump(),
        vehicle_id=vehicle_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    
    if commit:
        await db.commit()
        # Após o commit, recarregamos o objeto com a relação do veículo
        await db.refresh(db_obj, attribute_names=["vehicle"])
        
    return db_obj


# --- FUNÇÃO CORRIGIDA ---
async def get_costs_by_vehicle(
    db: AsyncSession, *, vehicle_id: int, skip: int = 0, limit: int = 100
) -> List[VehicleCost]:
    """Busca a lista de custos para um veículo específico, incluindo os dados do veículo."""
    stmt = (
        select(VehicleCost)
        .where(VehicleCost.vehicle_id == vehicle_id)
        .options(selectinload(VehicleCost.vehicle))  # <-- A CORREÇÃO ESTÁ AQUI
        .order_by(VehicleCost.date.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
# --- FIM DA CORREÇÃO ---


async def get_costs_by_organization(
    db: AsyncSession, 
    *, 
    organization_id: int, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[VehicleCost]:
    """Busca a lista de custos para uma organização inteira, com filtros de data."""
    stmt = (
        select(VehicleCost)
        .where(VehicleCost.organization_id == organization_id)
        .options(selectinload(VehicleCost.vehicle))
        .order_by(VehicleCost.date.desc())
    )
    
    if start_date:
        stmt = stmt.where(VehicleCost.date >= start_date)
    if end_date:
        stmt = stmt.where(VehicleCost.date <= end_date)
        
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()