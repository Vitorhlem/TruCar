from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.fuel_log_schema import FuelLogPublic, FuelLogCreate, FuelLogUpdate

router = APIRouter()

# --- ESTE ARQUIVO AGORA LIDA APENAS COM OPERAÇÕES MANUAIS ---

@router.post("/", response_model=FuelLogPublic, status_code=status.HTTP_201_CREATED)
async def create_fuel_log(
    *,
    db: AsyncSession = Depends(deps.get_db),
    log_in: FuelLogCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Registra um novo abastecimento para o utilizador logado."""
    return await crud.fuel_log.create_fuel_log(
        db=db, log_in=log_in, user_id=current_user.id, organization_id=current_user.organization_id
    )

@router.get("/", response_model=List[FuelLogPublic])
async def read_fuel_logs(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Retorna o histórico de abastecimentos."""
    if current_user.role in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        return await crud.fuel_log.get_multi_by_org(
            db=db, organization_id=current_user.organization_id, skip=skip, limit=limit
        )
    else: # DRIVER
        return await crud.fuel_log.get_multi_by_user(
            db=db, user_id=current_user.id, organization_id=current_user.organization_id, skip=skip, limit=limit
        )

@router.get("/{log_id}", response_model=FuelLogPublic)
async def read_fuel_log_by_id(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    log = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    return log

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fuel_log(
    log_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    log_to_delete = await crud.fuel_log.get_fuel_log(db, log_id=log_id, organization_id=current_user.organization_id)
    if not log_to_delete:
        raise HTTPException(status_code=404, detail="Registo de abastecimento não encontrado.")
    
    await crud.fuel_log.remove_fuel_log(db, db_obj=log_to_delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

