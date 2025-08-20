from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.fuel_log_schema import FuelLogPublic, FuelLogCreate

router = APIRouter()

@router.post("/", response_model=FuelLogPublic, status_code=status.HTTP_201_CREATED)
async def create_fuel_log_entry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    log_in: FuelLogCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Registra um novo abastecimento."""
    return await crud.fuel_log.create_fuel_log(
        db=db, log_in=log_in, user_id=current_user.id, organization_id=current_user.organization_id
    )

@router.get("/", response_model=List[FuelLogPublic])
async def read_fuel_logs(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retorna o histórico de abastecimentos.
    - Gestores (Managers) veem todos os registos da sua organização.
    - Motoristas (Drivers) veem apenas os seus próprios registos.
    """
    if current_user.role == UserRole.MANAGER:
        # CORREÇÃO AQUI: Passamos o organization_id do gestor
        return await crud.fuel_log.get_all_fuel_logs(db=db, organization_id=current_user.organization_id)
    else:
        return await crud.fuel_log.get_fuel_logs_by_user(db=db, user_id=current_user.id, organization_id=current_user.organization_id)