from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime

# Importações baseadas na estrutura do seu projeto
from app import deps
from app.models.vehicle_model import Vehicle
from app.models.location_history_model import LocationHistory
from app.models.alert_model import Alert 
from app.services.geofence_service import GeofenceService
from app.schemas.telemetry_schema import TelemetryBatch

router = APIRouter()

@router.post("/sync")
async def sync_telemetry(
    batch: TelemetryBatch,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Sincroniza dados de telemetria.
    Aceita PLACA ou ID do veículo no campo vehicle_token.
    """
    
    # --- LÓGICA HÍBRIDA DE BUSCA (AQUI ESTÁ A SOLUÇÃO) ---
    # Se o token for numérico (ex: "1"), buscamos pelo ID.
    # Se for texto (ex: "AGRO-01" ou "ABC-1234"), buscamos pela placa.
    
    query = select(Vehicle)
    
    if batch.vehicle_token.isdigit():
        # Busca por ID (converte string "1" para int 1)
        query = query.where(Vehicle.id == int(batch.vehicle_token))
    else:
        # Busca por Placa
        query = query.where(Vehicle.license_plate == batch.vehicle_token)
        
    result = await db.execute(query)
    vehicle = result.scalars().first()
    
    if not vehicle:
        # Debug: Mostra no log do servidor o que falhou
        print(f"❌ Erro Sync: Veículo não encontrado. Token recebido: {batch.vehicle_token}")
        raise HTTPException(status_code=404, detail=f"Veículo com token '{batch.vehicle_token}' não encontrado")

    last_point = None
    points_saved = 0
    
    # Processa os pontos
    for point in batch.points:
        # Validação básica de data (ignora datas muito antigas/erradas do GPS)
        point_time = datetime.fromtimestamp(point.timestamp)
        if point_time.year < 2024: 
            continue # Pula dados com data inválida (erro comum de GPS frio)

        # Salva histórico
        history = LocationHistory(
            vehicle_id=vehicle.id,
            latitude=point.latitude,
            longitude=point.longitude,
            speed=point.speed,
            timestamp=point_time
        )
        db.add(history)
        
        # Detecção de Buraco (MPU)
        if point.pothole_detected:
            pothole_alert = Alert(
                vehicle_id=vehicle.id,
                type="POTHOLE",
                severity="Medium",
                description=f"Impacto via detectado (Z: {point.acc_z:.2f})",
                latitude=point.latitude,
                longitude=point.longitude,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(pothole_alert)
            print(f"🕳️ Buraco detectado Veículo {vehicle.id}: {point.latitude}, {point.longitude}")

        # Checagem de Geofence (Cerca Virtual)
        # Executa em background ou await direto dependendo da performance desejada
        await GeofenceService.check_geofences(
            db, vehicle.id, point.latitude, point.longitude
        )

        last_point = point
        points_saved += 1

    # Atualiza posição atual do veículo (cache)
    if last_point:
        vehicle.last_latitude = last_point.latitude
        vehicle.last_longitude = last_point.longitude
        vehicle.last_updated = datetime.utcnow()
        # Se speed vier do GPS, atualizamos status
        if last_point.speed and last_point.speed > 0:
            vehicle.status = "active"
        else:
            vehicle.status = "stopped"
            
        db.add(vehicle)

    await db.commit()
    
    return {
        "status": "synced", 
        "vehicle_id": vehicle.id, 
        "points_received": len(batch.points),
        "points_saved": points_saved
    }