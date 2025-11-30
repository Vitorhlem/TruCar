from fastapi import APIRouter, Depends, Response, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, deps
from app.schemas.telemetry_schema import TelemetryPayload, TelemetryPacket
from app.models.alert_model import AlertLevel, AlertType
from app.schemas.alert_schema import AlertCreate
from app.models.location_history_model import LocationHistory

router = APIRouter()

# --- ENDPOINT 1: TELEMETRIA EM LOTE (TruCar Box / App Offline) ---
@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_telemetry_data(
    packet: TelemetryPacket,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Recebe um pacote com histórico de Rota + Eventos (Buracos/Velocidade).
    Usado pelo ESP32 e pelo Modo Offline do Celular.
    """
    print(f"📡 [SYNC] Recebendo {len(packet.points)} pontos do Veículo {packet.vehicle_id}")

    # 1. Salvar Histórico de Localização (Rastro Azul)
    if packet.points:
        last_pt = packet.points[-1]
        
        for pt in packet.points:
            if pt.lat != 0 and pt.lng != 0:
                loc = LocationHistory(
                    vehicle_id=packet.vehicle_id,
                    latitude=pt.lat,
                    longitude=pt.lng,
                    speed=pt.spd
                    # timestamp=datetime.fromtimestamp(pt.ts/1000)
                )
                db.add(loc)
        
        # Atualiza a posição atual do veículo
        vehicle = await crud.vehicle.get(db, vehicle_id=packet.vehicle_id, organization_id=1) # ID Org 1 (Demo)
        if vehicle:
            vehicle.last_latitude = last_pt.lat
            vehicle.last_longitude = last_pt.lng
            
            # Atualiza odômetro aproximado (simplificado)
            # Em produção, calcularíamos a distância entre os pontos
            db.add(vehicle)

    # 2. Processar Eventos e Gerar Alertas
    for evt in packet.events:
        if evt.lat == 0: continue

        alert_data = {
            "latitude": evt.lat,
            "longitude": evt.lng,
            "vehicle_id": packet.vehicle_id,
            "organization_id": 1, # ID Org 1 (Demo)
            "driver_id": None # Se tiver driver na journey, adicionar aqui
        }

        if evt.type == 'POTHOLE':
            alert_data.update({
                "message": f"Buraco Detectado (Impacto {evt.val:.1f})",
                "level": AlertLevel.WARNING if evt.val < 20 else AlertLevel.CRITICAL,
                "type": AlertType.ROAD_HAZARD
            })
        elif evt.type == 'SPEEDING':
            alert_data.update({
                "message": f"Excesso de Velocidade ({evt.val:.0f} km/h)",
                "level": AlertLevel.CRITICAL,
                "type": AlertType.SPEEDING
            })
        
        # Usa o Schema AlertCreate para validar
        await crud.alert.create(db, obj_in=AlertCreate(**alert_data))

    await db.commit()
    return {"status": "synced", "points": len(packet.points), "events": len(packet.events)}


# --- ENDPOINT 2: TELEMETRIA SIMPLES (Legado / Tempo Real Unitário) ---
@router.post("/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_telemetry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    payload: TelemetryPayload
):
    """Recebe, processa telemetria unitária e GERA ALERTAS."""
    
    # 1. Atualiza o veículo
    vehicle = await crud.vehicle.update_vehicle_from_telemetry(db=db, payload=payload)
    if not vehicle:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    
    # 2. Lógica de Manutenção
    if vehicle.next_maintenance_km and vehicle.current_km:
        if vehicle.current_km >= vehicle.next_maintenance_km:
            alert_msg = f"Manutenção Vencida: Veículo atingiu {vehicle.current_km:.0f}km (Prazo: {vehicle.next_maintenance_km:.0f}km)"
            await crud.alert.create(db=db, obj_in=AlertCreate(
                message=alert_msg,
                level=AlertLevel.WARNING,
                type=AlertType.MAINTENANCE,
                organization_id=vehicle.organization_id,
                vehicle_id=vehicle.id,
                driver_id=vehicle.current_driver_id
            ))
    
    # 3. Lógica de Velocidade
    MAX_SPEED_LIMIT = 110.0
    if payload.speed and payload.speed > MAX_SPEED_LIMIT:
        await crud.alert.create(db=db, obj_in=AlertCreate(
            message=f"Excesso de velocidade: {payload.speed} km/h",
            level=AlertLevel.CRITICAL,
            type=AlertType.SPEEDING,
            organization_id=vehicle.organization_id,
            vehicle_id=vehicle.id,
            driver_id=vehicle.current_driver_id,
            latitude=payload.latitude,
            longitude=payload.longitude
        ))

    # 4. Lógica de Temperatura
    if payload.engine_temp and payload.engine_temp > 105:
        await crud.alert.create(db=db, obj_in=AlertCreate(
            message=f"Superaquecimento do motor: {payload.engine_temp}°C",
            level=AlertLevel.WARNING,
            type=AlertType.GENERIC,
            organization_id=vehicle.organization_id,
            vehicle_id=vehicle.id,
            driver_id=vehicle.current_driver_id
        ))

    return Response(status_code=status.HTTP_204_NO_CONTENT)