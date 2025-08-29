# ARQUIVO: backend/app/api/v1/endpoints/vehicles.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.vehicle_schema import (
    VehicleCreate, 
    VehicleUpdate, 
    VehiclePublic, 
    VehicleListResponse
)

router = APIRouter()


@router.get("/", response_model=VehicleListResponse)
async def read_vehicles(
    db: AsyncSession = Depends(deps.get_db),
    page: int = 1,
    rowsPerPage: int = 8,
    search: str | None = None,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Lista os veículos da organização com paginação e busca.
    """
    skip = (page - 1) * rowsPerPage
    
    vehicles = await crud.vehicle.get_multi_by_org(
        db,
        organization_id=current_user.organization_id,
        skip=skip,
        limit=rowsPerPage,
        search=search
    )
    total_items = await crud.vehicle.count_by_org(
        db,
        organization_id=current_user.organization_id,
        search=search
    )

    return {"vehicles": vehicles, "total_items": total_items}


@router.get("/{vehicle_id}", response_model=VehiclePublic)
async def read_vehicle_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Busca um único veículo pelo ID.
    """
    # --- CORREÇÃO: Chama a função padronizada 'get' ---
    vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    return vehicle


@router.post("/", response_model=VehiclePublic, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Cria um novo veículo para a organização do gestor logado.
    """
    # A verificação de placa duplicada pode ser adicionada ao CRUD se necessário,
    # ou podemos confiar na restrição UNIQUE do banco de dados.
    # Por simplicidade, vamos chamar a função de criação padronizada.
    
    # --- CORREÇÃO: Chama a função padronizada 'create_with_owner' ---
    vehicle = await crud.vehicle.create_with_owner(
        db=db, obj_in=vehicle_in, organization_id=current_user.organization_id
    )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehiclePublic)
async def update_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    vehicle_in: VehicleUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Atualiza um veículo.
    """
    # Primeiro, busca o veículo para garantir que ele existe e pertence à organização
    db_vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
    # --- CORREÇÃO: Chama a função padronizada 'update' ---
    updated_vehicle = await crud.vehicle.update(db=db, db_vehicle=db_vehicle, vehicle_in=vehicle_in)
    return updated_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Exclui um veículo.
    """
    # Primeiro, busca o veículo para garantir que ele existe
    db_vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
    # --- CORREÇÃO: Chama a função padronizada 'remove' ---
    await crud.vehicle.remove(db=db, db_vehicle=db_vehicle)
    return Response(status_code=status.HTTP_204_NO_CONTENT)