from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import crud, deps
from app.models.user_model import User
from app.schemas.vehicle_component_schema import VehicleComponentCreate, VehicleComponentPublic

router = APIRouter()


@router.get("/vehicles/{vehicle_id}/components", response_model=List[VehicleComponentPublic])
async def read_components_for_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Busca o histórico de componentes instalados em um veículo.
    (Este endpoint de LEITURA está correto)
    """
    vehicle = await crud.vehicle.get(db, vehicle_id=vehicle_id, organization_id=current_user.organization_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    components = await crud.vehicle_component.get_components_by_vehicle(db=db, vehicle_id=vehicle_id)
    return components


@router.post("/vehicles/{vehicle_id}/components", response_model=VehicleComponentPublic, status_code=status.HTTP_201_CREATED)
async def install_vehicle_component(
    vehicle_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    obj_in: VehicleComponentCreate,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Instala um novo componente em um veículo.
    (CORRIGIDO com Commit-e-Refetch)
    """
    try:
        # 1. CRUD (NÃO FAZ COMMIT)
        new_component = await crud.vehicle_component.install_component(
            db=db,
            vehicle_id=vehicle_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            obj_in=obj_in
        )
        component_id = new_component.id
        
        # 2. ENDPOINT FAZ COMMIT
        await db.commit()
        
        # 3. Recarregamos o componente com todos os dados para a API
        reloaded_component = await crud.vehicle_component.get_component_for_api(
            db=db, component_id=component_id
        )
        return reloaded_component
        
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao instalar componente: {e}")


@router.put("/vehicle-components/{component_id}/discard", response_model=VehicleComponentPublic)
async def discard_vehicle_component(
    component_id: int,
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Marca um componente como 'descartado' (Fim de Vida).
    (CORRIGIDO com Commit-e-Refetch)
    """
    try:
        # 1. CRUD (NÃO FAZ COMMIT)
        discarded_component = await crud.vehicle_component.discard_component(
            db=db,
            component_id=component_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id
        )
        
        # 2. ENDPOINT FAZ COMMIT
        await db.commit()
        
        # 3. Recarregamos o componente com todos os dados para a API
        reloaded_component = await crud.vehicle_component.get_component_for_api(
            db=db, component_id=discarded_component.id
        )
        return reloaded_component

    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao descartar componente: {e}")