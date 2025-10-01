from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.tire_schema import TireLayoutResponse, TireInstall

router = APIRouter()

@router.get("/vehicles/{vehicle_id}/tires", response_model=TireLayoutResponse)
async def get_vehicle_tire_layout(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Retorna a configuração atual de pneus para um veículo."""
    vehicle = await crud.vehicle.get(db, vehicle_id=vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    
    tires = await crud.tire.get_active_tires_by_vehicle(db=db, vehicle_id=vehicle_id)
    return {"vehicle_id": vehicle.id, "axle_configuration": vehicle.axle_configuration, "tires": tires}

@router.post("/vehicles/{vehicle_id}/tires", status_code=status.HTTP_201_CREATED)
async def install_tire_on_vehicle(
    vehicle_id: int,
    tire_in: TireInstall,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Instala um pneu do inventário em uma posição do veículo."""
    try:
        await crud.tire.install_tire(
            db=db,
            vehicle_id=vehicle_id,
            part_id=tire_in.part_id,
            position_code=tire_in.position_code,
            install_km=tire_in.install_km,
            user_id=current_user.id
        )
        return {"message": "Pneu instalado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/tires/{tire_id}/remove", status_code=status.HTTP_200_OK)
async def remove_tire_from_vehicle(
    tire_id: int,
    removal_km: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Remove (descarta) um pneu de um veículo."""
    try:
        await crud.tire.remove_tire(
            db=db,
            tire_id=tire_id,
            removal_km=removal_km,
            user_id=current_user.id
        )
        return {"message": "Pneu removido e descartado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))