from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# --- CORREÇÃO AQUI: Importar deps diretamente de app, não de app.api ---
from app import deps 
from app.services.weather_intelligence import WeatherIntelligenceService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class WeatherEventSchema(BaseModel):
    id: int
    event_type: str
    description: str
    severity: str
    affected_lat: float
    affected_lon: float
    affected_radius_km: float
    detected_at: datetime

    class Config:
        from_attributes = True

@router.get("/alerts", response_model=List[WeatherEventSchema])
async def read_weather_alerts(
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retorna alertas climáticos ativos.
    """
    # Analisa risco em tempo real
    active_risks = await WeatherIntelligenceService.analyze_active_journeys(db)
    return active_risks