# backend/app/api/v1/endpoints/telemetry.py
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, deps
from app.schemas.telemetry_schema import TelemetryPayload
from app.models.alert_model import AlertLevel # Importar o Enum
from app.schemas.alert_schema import AlertCreate # Importar o Schema criado

router = APIRouter()

@router.post("/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_telemetry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    payload: TelemetryPayload
):
    """Recebe, processa telemetria e GERA ALERTAS."""
    
    # 1. Atualiza o veículo (lógica existente)
    vehicle = await crud.vehicle.update_vehicle_from_telemetry(db=db, payload=payload)
    
    # 2. Lógica de Geração de Alerta (Exemplo: Excesso de Velocidade)
    MAX_SPEED_LIMIT = 110.0

    if vehicle.next_maintenance_km and vehicle.current_km:
        # Se rodou mais que o previsto
        if vehicle.current_km >= vehicle.next_maintenance_km:
            # Verifica se já existe alerta pendente para não spammar (simplificado)
            # Em produção, você verificaria se o último alerta desse tipo foi há X horas
            
            alert_msg = f"Manutenção Vencida: Veículo atingiu {vehicle.current_km:.0f}km (Prazo: {vehicle.next_maintenance_km:.0f}km)"
            
            # Criamos o alerta usando o CRUD que criamos
            await crud.alert.create(db=db, obj_in=AlertCreate(
                message=alert_msg,
                level=AlertLevel.WARNING,
                organization_id=vehicle.organization_id,
                vehicle_id=vehicle.id,
                driver_id=vehicle.current_driver_id
            ))
    
    if payload.speed and payload.speed > MAX_SPEED_LIMIT:
        # Verifica se já existe um alerta recente para não spammar (opcional, simplificado aqui)
        
        alert_data = AlertCreate(
            message=f"Excesso de velocidade detectado: {payload.speed} km/h",
            level=AlertLevel.CRITICAL, #
            organization_id=vehicle.organization_id, # Pega do veículo recuperado
            vehicle_id=vehicle.id,
            driver_id=vehicle.current_driver_id # Se o veículo tiver motorista associado
        )
        
        await crud.alert.create(db=db, obj_in=alert_data)

    # 3. Lógica de Temperatura (Exemplo)
    if payload.engine_temp and payload.engine_temp > 105:
        alert_data = AlertCreate(
            message=f"Superaquecimento do motor: {payload.engine_temp}°C",
            level=AlertLevel.WARNING,
            organization_id=vehicle.organization_id,
            vehicle_id=vehicle.id,
            driver_id=vehicle.current_driver_id
        )
        await crud.alert.create(db=db, obj_in=alert_data)

    return Response(status_code=status.HTTP_204_NO_CONTENT)