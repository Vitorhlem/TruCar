from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehiclePublic, PaginatedVehicles

router = APIRouter()

@router.post("/", response_model=VehiclePublic, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Cria um novo veículo para a organização do gestor logado."""
    if vehicle_in.license_plate:
        # Passa o organization_id para a verificação de duplicados
        existing_vehicle = await crud.vehicle.get_vehicle_by_license_plate(
            db, license_plate=vehicle_in.license_plate, organization_id=current_user.organization_id
        )
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Um veículo com a placa {vehicle_in.license_plate} já está cadastrado nesta organização."
            )
            
    vehicle = await crud.vehicle.create_vehicle(
        db=db, vehicle_in=vehicle_in, organization_id=current_user.organization_id
    )
    return vehicle

@router.get("/", response_model=PaginatedVehicles)
async def read_vehicles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 8,
    search: str | None = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Retorna uma lista paginada de veículos da organização do usuário."""
    vehicles, total_count = await crud.vehicle.get_multi_by_org(
        db, 
        organization_id=current_user.organization_id, 
        skip=skip, 
        limit=limit, 
        search=search
    )
    return {"total": total_count, "items": vehicles}

@router.get("/{vehicle_id}", response_model=VehiclePublic)
async def read_vehicle_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Busca um único veículo pelo ID."""
    vehicle = await crud.vehicle.get_vehicle(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    return vehicle

@router.put("/{vehicle_id}", response_model=VehiclePublic)
async def update_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Atualiza um veículo."""
    db_vehicle = await crud.vehicle.get_vehicle(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
    updated_vehicle = await crud.vehicle.update_vehicle(db=db, db_vehicle=db_vehicle, vehicle_in=vehicle_in)
    return updated_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Exclui um veículo."""
    db_vehicle = await crud.vehicle.get_vehicle(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
    await crud.vehicle.delete_vehicle(db=db, db_vehicle=db_vehicle)
    return Response(status_code=status.HTTP_204_NO_CONTENT)