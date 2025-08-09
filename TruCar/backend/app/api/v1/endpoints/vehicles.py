from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehiclePublic

router = APIRouter()

@router.post("/", response_model=VehiclePublic, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_in: VehicleCreate,
    # A LINHA ABAIXO É A TRAVA DE SEGURANÇA. SÓ MANAGERS PASSAM DAQUI.
    current_user: User = Depends(deps.get_current_active_manager)
) -> any:
    existing_vehicle = await crud.vehicle.get_vehicle_by_license_plate(db, license_plate=vehicle_in.license_plate)
    if existing_vehicle:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Um veículo com a placa {vehicle_in.license_plate} já está cadastrado.")
    vehicle = await crud.vehicle.create_vehicle(db=db, vehicle_in=vehicle_in)
    return vehicle

# ... (o resto do arquivo, com GET, PUT, DELETE, continua o mesmo) ...

@router.get("/", response_model=List[VehiclePublic])
async def read_vehicles(db: AsyncSession = Depends(deps.get_db), skip: int = 0, limit: int = 100, current_user: User = Depends(deps.get_current_active_user)) -> any:
    vehicles = await crud.vehicle.get_all_vehicles(db, skip=skip, limit=limit)
    return vehicles

@router.get("/{vehicle_id}", response_model=VehiclePublic)
async def read_vehicle(*, db: AsyncSession = Depends(deps.get_db), vehicle_id: int, current_user: User = Depends(deps.get_current_active_user)) -> any:
    vehicle = await crud.vehicle.get_vehicle(db, vehicle_id=vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    return vehicle

@router.put("/{vehicle_id}", response_model=VehiclePublic)
async def update_vehicle(*, db: AsyncSession = Depends(deps.get_db), vehicle_id: int, vehicle_in: VehicleUpdate, current_user: User = Depends(deps.get_current_active_manager)) -> any:
    db_vehicle = await crud.vehicle.get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    updated_vehicle = await crud.vehicle.update_vehicle(db=db, db_vehicle=db_vehicle, vehicle_in=vehicle_in)
    return updated_vehicle

@router.delete("/{vehicle_id}", response_model=VehiclePublic)
async def delete_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
) -> any:
    db_vehicle = await crud.vehicle.get_vehicle(db, vehicle_id=vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    try:
        deleted_vehicle = await crud.vehicle.delete_vehicle(db=db, db_vehicle=db_vehicle)
        return deleted_vehicle
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir um veículo que já possui viagens registradas.",
        )