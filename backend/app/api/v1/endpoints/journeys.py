from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date

from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate, JourneyPublic, EndJourneyResponse
from app.crud.crud_journey import VehicleNotAvailableError # Importa a exceção customizada

router = APIRouter()

@router.get("/", response_model=List[JourneyPublic])
async def read_journeys(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0, limit: int = 100, driver_id: int | None = None,
    vehicle_id: int | None = None, date_from: date | None = None,
    date_to: date | None = None, current_user: User = Depends(deps.get_current_active_user)
):
    """Lista todas as viagens da organização, aplicando limites de demo se necessário."""
    if date_to and date_from and date_to < date_from:
        raise HTTPException(status_code=400, detail="A data final não pode ser anterior à data inicial.")
    
    final_driver_id_filter = driver_id
    if current_user.role == UserRole.DRIVER and not driver_id:
        final_driver_id_filter = current_user.id
        
    journeys = await crud.journey.get_all_journeys(
        db, 
        organization_id=current_user.organization_id,
        requester_role=current_user.role,  # <-- PASSAMOS O PAPEL DO UTILIZADOR
        skip=skip, 
        limit=limit, 
        driver_id=final_driver_id_filter,
        vehicle_id=vehicle_id, 
        date_from=date_from, 
        date_to=date_to
    )
    return journeys

@router.post("/start", response_model=JourneyPublic, status_code=status.HTTP_201_CREATED)
async def start_journey(
    *,
    db: AsyncSession = Depends(deps.get_db),
    journey_in: JourneyCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Inicia uma nova viagem para o utilizador logado."""
    # --- LÓGICA DE LIMITE DE DEMO ADICIONADA ---
    # Se o utilizador for um CLIENTE_DEMO, verificamos o limite mensal
    if current_user.role == UserRole.CLIENTE_DEMO:
        monthly_journeys = await crud.journey.count_journeys_in_current_month(
            db, organization_id=current_user.organization_id
        )
        if monthly_journeys >= 10:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="A sua conta de demonstração permite o registo de 10 jornadas por mês. Faça o upgrade para continuar."
            )
    # --- FIM DA LÓGICA DE LIMITE ---

    existing_journey = await crud.journey.get_active_journey_by_driver(
        db, driver_id=current_user.id, organization_id=current_user.organization_id
    )
    if existing_journey:
        raise HTTPException(status_code=400, detail="O motorista já tem uma operação ativa.")
    
    try:
        journey = await crud.journey.create_journey(
            db, journey_in=journey_in, driver_id=current_user.id,
            organization_id=current_user.organization_id
        )
        return journey
    except VehicleNotAvailableError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
@router.put("/{journey_id}/end", response_model=EndJourneyResponse)
async def end_journey(
    *,
    db: AsyncSession = Depends(deps.get_db),
    journey_id: int,
    journey_in: JourneyUpdate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Finaliza uma viagem."""
    journey_to_end = await crud.journey.get_journey(
        db, journey_id=journey_id, organization_id=current_user.organization_id
    )
    if not journey_to_end:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    if not journey_to_end.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta viagem já foi finalizada.")
    if journey_to_end.driver_id != current_user.id and current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Apenas o motorista da viagem ou um gestor podem finalizá-la.")
    
    finished_journey, updated_vehicle = await crud.journey.end_journey(
        db=db, db_journey=journey_to_end, journey_in=journey_in
    )
    return {"journey": finished_journey, "vehicle": updated_vehicle}

@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journey(
    *,
    db: AsyncSession = Depends(deps.get_db),
    journey_id: int,
    current_user: User = Depends(deps.get_current_active_manager)
):
    """Exclui uma viagem (apenas para gestores)."""
    journey_to_delete = await crud.journey.get_journey(
        db, journey_id=journey_id, organization_id=current_user.organization_id
    )
    if not journey_to_delete:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    
    await crud.journey.delete_journey(db=db, journey_to_delete=journey_to_delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)