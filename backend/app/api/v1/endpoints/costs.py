# Em backend/app/api/v1/endpoints/costs.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.vehicle_cost_schema import VehicleCostPublic

router = APIRouter()

@router.get("/", response_model=List[VehicleCostPublic])
async def read_organization_costs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Lista todos os custos da organização do usuário logado, com filtros opcionais.
    """
    costs = await crud.vehicle_cost.get_costs_by_organization(
        db, 
        organization_id=current_user.organization_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    return costs