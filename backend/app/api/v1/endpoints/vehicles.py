from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
# --- ADICIONADO ---
# Importamos o Enum para verificar o status do plano da organização
# --- FIM DA ADIÇÃO ---
from sqlalchemy.exc import IntegrityError

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
    # --- LÓGICA DE RESTRIÇÃO ATUALIZADA ---
    # Agora a verificação é feita sobre o PAPEL do utilizador, não sobre a organização.
    if current_user.role == UserRole.CLIENTE_DEMO:
        vehicle_count = await crud.vehicle.count_by_org(db, organization_id=current_user.organization_id)
        if vehicle_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A sua conta de demonstração permite o cadastro de apenas 1 veículo."
            )
    # --- FIM DA ATUALIZAÇÃO ---

    try:
        vehicle = await crud.vehicle.create_with_owner(
            db=db, obj_in=vehicle_in, organization_id=current_user.organization_id
        )
        return vehicle
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Um veículo com esta placa ou identificador já existe na sua organização.",
        )



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
    db_vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
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
    db_vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    
    await crud.vehicle.remove(db=db, db_vehicle=db_vehicle)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
