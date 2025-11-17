from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, deps
from app.schemas.tire_schema import TireLayoutResponse, TireInstall, TireRemove, VehicleTireHistory

router = APIRouter()

@router.get("/vehicles/{vehicle_id}/tires", response_model=TireLayoutResponse)
async def get_vehicle_tire_layout(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
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
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Instala um pneu do inventário em uma posição do veículo."""
    try:
        await crud.tire.install_tire(
            db=db, vehicle_id=vehicle_id, part_id=tire_in.part_id,
            position_code=tire_in.position_code, install_km=tire_in.install_km,
            install_engine_hours=tire_in.install_engine_hours, user_id=current_user.id
        )
        return {"message": "Pneu instalado com sucesso."}
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        print(f"Erro inesperado ao instalar pneu: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao instalar o pneu.")


@router.put("/tires/{tire_id}/remove", status_code=status.HTTP_200_OK)
async def remove_tire_from_vehicle(
    tire_id: int,
    removal_data: TireRemove,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Remove (descarta) um pneu de um veículo."""
    try:
        await crud.tire.remove_tire(
            db=db, tire_id=tire_id, removal_km=removal_data.removal_km,
            removal_engine_hours=removal_data.removal_engine_hours, user_id=current_user.id
        )
        return {"message": "Pneu removido e descartado com sucesso."}
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        print(f"Erro inesperado ao remover pneu: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao remover o pneu.")

@router.get("/vehicles/{vehicle_id}/removed-tires", response_model=list[VehicleTireHistory])
async def get_removed_tires_history(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    """Obtém o histórico de pneus removidos para um veículo específico."""
    history_db = await crud.tire.get_removed_tires_for_vehicle(db=db, vehicle_id=vehicle_id)
    
    response = [VehicleTireHistory.model_validate(tire) for tire in history_db]
    
    return response