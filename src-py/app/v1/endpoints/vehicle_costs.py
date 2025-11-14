from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, deps
from app.models.user_model import User
from app.schemas.vehicle_cost_schema import VehicleCostCreate, VehicleCostPublic

router = APIRouter()


@router.get("/", response_model=List[VehicleCostPublic])
async def read_vehicle_costs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Lista todos os custos associados a um veículo específico.
    """
    # Primeiro, verificamos se o veículo pertence à organização do utilizador
    vehicle = await crud.vehicle.get(db, vehicle_id=vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado nesta organização."
        )
    
    costs = await crud.vehicle_cost.get_costs_by_vehicle(
        db, vehicle_id=vehicle_id, skip=skip, limit=limit
    )
    return costs


@router.post("/", response_model=VehicleCostPublic, status_code=status.HTTP_201_CREATED)
async def create_vehicle_cost(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    cost_in: VehicleCostCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Cria um novo registo de custo para um veículo específico.
    """
    # Verificamos novamente se o veículo pertence à organização do utilizador
    vehicle = await crud.vehicle.get(db, vehicle_id=vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado nesta organização."
        )

    cost = await crud.vehicle_cost.create_cost(
        db, obj_in=cost_in, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    return cost