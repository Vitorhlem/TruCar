from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from app.models.notification_model import NotificationType
from app.schemas.audit_log_schema import AuditLogCreate
from app.crud import crud_audit_log
from app import crud, deps
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
    background_tasks: BackgroundTasks,
    journey_in: JourneyCreate,
    current_user: User = Depends(deps.get_current_active_user)
):
    """Inicia uma nova viagem para o utilizador logado (ILIMITADO PARA DEMO)."""
    
    # --- REMOVIDA A VERIFICAÇÃO DE LIMITE MENSAL AQUI ---
    
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
        
        # Opcional: Ainda podemos incrementar o contador para estatísticas, mas sem bloquear
        if current_user.role == UserRole.CLIENTE_DEMO:
             await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="journeys")

        message = f"{current_user.full_name} iniciou uma nova jornada com {journey.vehicle.brand} {journey.vehicle.model}."
        background_tasks.add_task(
            crud.notification.create_notification,
            db=db,
            message=message,
            notification_type=NotificationType.JOURNEY_STARTED,
            organization_id=current_user.organization_id,
            send_to_managers=True,
            related_entity_type="journey",
            related_entity_id=journey.id,
            related_vehicle_id=journey.vehicle.id
        )

        try:
            await crud_audit_log.create(db=db, log_in=AuditLogCreate(
                action="CREATE", resource_type="Registro de Viagem", resource_id=str(journey.id),
                user_id=current_user.id, organization_id=current_user.organization_id,
                details={"vehicle_id": journey.vehicle_id, "start_km": journey.start_mileage}
            ))
            await db.commit()
        except Exception as e:
            print(f"Erro auditoria: {e}")
        
        return journey
    except (VehicleNotAvailableError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{journey_id}/end", response_model=EndJourneyResponse)
async def end_journey(
    *,
    db: AsyncSession = Depends(deps.get_db),
    background_tasks: BackgroundTasks,
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
    if journey_to_end.driver_id != current_user.id and current_user.role not in [UserRole.CLIENTE_ATIVO, UserRole.CLIENTE_DEMO]:
        raise HTTPException(status_code=403, detail="Apenas o motorista da viagem ou um gestor podem finalizá-la.")
    
    finished_journey, updated_vehicle = await crud.journey.end_journey(
        db=db, db_journey=journey_to_end, journey_in=journey_in
    )

    if updated_vehicle:
        message = f"{current_user.full_name} finalizou a jornada com {updated_vehicle.brand} {updated_vehicle.model}."
        background_tasks.add_task(
            crud.notification.create_notification,
            db=db,
            message=message,
            notification_type=NotificationType.JOURNEY_ENDED,
            organization_id=current_user.organization_id,
            send_to_managers=True,
            related_entity_type="journey",
            related_entity_id=finished_journey.id,
            related_vehicle_id=updated_vehicle.id
        )

    try:
        await crud_audit_log.create(db=db, log_in=AuditLogCreate(
            action="UPDATE", resource_type="Registro de Viagem", resource_id=str(finished_journey.id),
            user_id=current_user.id, organization_id=current_user.organization_id,
            details={"action": "finish_journey", "end_km": journey_in.end_mileage}
        ))
        await db.commit()
    except Exception as e:
        print(f"Erro auditoria: {e}")

    return EndJourneyResponse(journey=finished_journey, vehicle=updated_vehicle)

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