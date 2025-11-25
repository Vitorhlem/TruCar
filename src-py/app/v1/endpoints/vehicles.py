from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel  # Importa BaseModel
from app.schemas.audit_log_schema import AuditLogCreate
from app.crud import crud_audit_log
from app import crud, deps
from app.models.user_model import User, UserRole
from sqlalchemy.exc import IntegrityError

from app.schemas.vehicle_schema import (
    VehicleCreate,
    VehicleUpdate,
    VehiclePublic,
    VehicleListResponse
)
from app.schemas.inventory_transaction_schema import TransactionPublic

router = APIRouter()

# --- NOVO SCHEMA PARA ATUALIZAÇÃO DO EIXO ---
class AxleConfigUpdate(BaseModel):
    axle_configuration: str

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

@router.get("/{vehicle_id}/inventory-history", response_model=List[TransactionPublic])
async def read_vehicle_inventory_history(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Retorna o histórico de todas as movimentações de peças/inventário
    associadas a um veículo específico.
    """
    vehicle = await crud.vehicle.get(db, vehicle_id=vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")

    history = await crud.inventory_transaction.get_transactions_by_vehicle_id(db, vehicle_id=vehicle_id)
    return history


@router.post("/", response_model=VehiclePublic, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(deps.check_demo_limit("vehicles"))])
async def create_vehicle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_in: VehicleCreate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Cria um novo veículo para a organização do gestor logado."""
    try:
        vehicle = await crud.vehicle.create_with_owner(
            db=db, obj_in=vehicle_in, organization_id=current_user.organization_id
        )

        try:
            await crud_audit_log.create(db=db, log_in=AuditLogCreate(
                action="CREATE", resource_type="Veículos", resource_id=str(vehicle.id),
                user_id=current_user.id, organization_id=current_user.organization_id,
                details={"plate": vehicle.license_plate, "model": vehicle.model}
            ))
            await db.commit()
        except Exception as e:
            print(f"Erro auditoria: {e}")

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

    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="UPDATE", resource_type="Veículos", resource_id=str(updated_vehicle.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"updates": vehicle_in.model_dump(exclude_unset=True)}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")

    return updated_vehicle


# --- NOVO ENDPOINT PARA ATUALIZAR A CONFIGURAÇÃO DE EIXOS ---
@router.patch("/{vehicle_id}/axle-config", response_model=VehiclePublic)
async def update_vehicle_axle_config(
    *,
    db: AsyncSession = Depends(deps.get_db),
    vehicle_id: int,
    config_in: AxleConfigUpdate,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """
    Atualiza a configuração de eixos de um veículo.
    """
    db_vehicle = await crud.vehicle.get(
        db, vehicle_id=vehicle_id, organization_id=current_user.organization_id
    )
    if not db_vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")

    db_vehicle.axle_configuration = config_in.axle_configuration
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle
# --- FIM DO NOVO ENDPOINT ---


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

    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="DELETE", resource_type="Veículos", resource_id=str(vehicle_id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"deleted_plate": db_vehicle.license_plate}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
