from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from pydantic import BaseModel

from app import deps
from app.models.vehicle_model import Vehicle
from app.models.location_history_model import LocationHistory
# Precisamos de um modelo para Buracos (pode ser o AlertModel ou um novo PotholeModel)
# Por enquanto, vou usar o Alert para simplificar
from app.models.alert_model import Alert 

router = APIRouter()

# --- SCHEMA QUE O ESP32 VAI ENVIAR ---
class TelemetryPoint(BaseModel):
    latitude: float
    longitude: float
    speed: Optional[float] = 0.0
    timestamp: int # Unix Timestamp do GPS
    pothole_detected: bool = False # MPU detectou impacto no eixo Z?
    acc_z: Optional[float] = 0.0   # Valor do acelerômetro (opcional)

class TelemetryBatch(BaseModel):
    vehicle_token: str # Token único do hardware (ou ID)
    points: List[TelemetryPoint]

@router.post("/sync")
async def sync_telemetry(
    batch: TelemetryBatch,
    db: AsyncSession = Depends(deps.get_db)
):
    """
    Recebe dados do Hardware (Real-time ou Offline Sync).
    Processa buracos e atualiza posição atual.
    """
    # 1. Identifica o Veículo pelo Token (Supondo que license_plate ou um campo token seja usado)
    # Aqui vou usar license_plate como exemplo simples, mas ideal é um token de API
    result = await db.execute(select(Vehicle).where(Vehicle.license_plate == batch.vehicle_token))
    vehicle = result.scalars().first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    last_point = None
    
    # 2. Processa a lista de pontos (Histórico)
    for point in batch.points:
        # Salva no histórico de rota
        history = LocationHistory(
            vehicle_id=vehicle.id,
            latitude=point.latitude,
            longitude=point.longitude,
            speed=point.speed,
            timestamp=datetime.fromtimestamp(point.timestamp)
        )
        db.add(history)
        
        # 3. DETECÇÃO DE BURACO (MPU)
        if point.pothole_detected:
            # Cria um alerta de via danificada
            pothole_alert = Alert(
                vehicle_id=vehicle.id,
                type="POTHOLE", # Novo tipo
                severity="Medium",
                description=f"Buraco detectado (Impacto Z: {point.acc_z})",
                latitude=point.latitude,
                longitude=point.longitude,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(pothole_alert)
            print(f"🕳️ BURACO REGISTRADO: {point.latitude}, {point.longitude}")

        last_point = point

    # 4. Atualiza a posição ATUAL do veículo com o último ponto recebido
    if last_point:
        vehicle.last_latitude = last_point.latitude
        vehicle.last_longitude = last_point.longitude
        vehicle.last_updated = datetime.utcnow()
        db.add(vehicle)

    await db.commit()
    return {"status": "synced", "points_processed": len(batch.points)}