from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app import deps
# --- CORREÇÃO 1: Importar VehicleStatus ---
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.models.location_history_model import LocationHistory
from app.models.alert_model import Alert 
from app.services.geofence_service import GeofenceService
from app.schemas.telemetry_schema import TelemetryBatch

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/sync")
async def sync_telemetry(
    batch: TelemetryBatch,
    db: AsyncSession = Depends(deps.get_db)
):
    try:
        # 1. Identificação do Veículo
        vehicle = None
        
        if batch.vehicle_id is not None:
            result = await db.execute(select(Vehicle).where(Vehicle.id == batch.vehicle_id))
            vehicle = result.scalars().first()
            
        if not vehicle and batch.vehicle_token:
            if batch.vehicle_token.isdigit():
                 result = await db.execute(select(Vehicle).where(Vehicle.id == int(batch.vehicle_token)))
                 vehicle = result.scalars().first()
            
            if not vehicle:
                result = await db.execute(select(Vehicle).where(Vehicle.license_plate == batch.vehicle_token))
                vehicle = result.scalars().first()

        if not vehicle:
            logger.error(f"Veículo não encontrado. ID: {batch.vehicle_id}")
            raise HTTPException(status_code=404, detail="Veículo não encontrado")

        points_saved = 0
        last_point = None

        # 2. Processa Pontos
        for p in batch.points:
            try:
                dt = datetime.fromtimestamp(p.ts)
                if dt.year < 2024: continue
            except:
                continue

            history = LocationHistory(
                vehicle_id=vehicle.id,
                latitude=p.lat,
                longitude=p.lng,
                speed=p.spd, 
                timestamp=dt
            )
            db.add(history)

            if p.pothole_detected:
                alert = Alert(
                    vehicle_id=vehicle.id,
                    type="POTHOLE",
                    severity="Medium",
                    description=f"Buraco detectado (Z: {p.acc_z})",
                    latitude=p.lat,
                    longitude=p.lng,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(alert)

            try:
                await GeofenceService.check_geofences(db, vehicle.id, p.lat, p.lng)
            except Exception as e:
                logger.warning(f"Erro ao checar geofence: {e}")

            last_point = p
            points_saved += 1

        # 3. Atualiza Posição e Status do Veículo
        if last_point:
            vehicle.last_latitude = last_point.lat
            vehicle.last_longitude = last_point.lng
            vehicle.last_updated = datetime.utcnow()
            
            # --- CORREÇÃO 2: Usar o Enum VehicleStatus ---
            # Se a velocidade for maior que 0, está "Em uso". 
            # Se for 0, está "Disponível" (ou parado).
            if last_point.spd and last_point.spd > 0:
                vehicle.status = VehicleStatus.IN_USE
            else:
                vehicle.status = VehicleStatus.AVAILABLE
                
            db.add(vehicle)

        await db.commit()
        return {"status": "ok", "saved": points_saved}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"ERRO CRÍTICO 500: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")