import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.models.journey_model import Journey

class WeatherIntelligenceService:
    
    @staticmethod
    async def fetch_weather_alerts(lat: float, lon: float):
        if not settings.OPENWEATHER_API_KEY:
             return None

        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,daily", 
            "appid": settings.OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=5.0)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Erro OpenWeather: {e}")
            return None

    @staticmethod
    async def analyze_location(lat: float, lon: float, context_id: str = "Location"):
        weather_data = await WeatherIntelligenceService.fetch_weather_alerts(lat, lon)
        if not weather_data:
            return None

        # 1. APENAS ALERTAS OFICIAIS (Segurança Real)
        if "alerts" in weather_data:
            for alert in weather_data["alerts"]:
                return {
                    "id": int(datetime.utcnow().timestamp()) + hash(context_id),
                    "event_type": alert.get("event", "Alerta Oficial"),
                    "severity": "Severe",
                    "description": alert.get("description", ""),
                    "affected_lat": lat,
                    "affected_lon": lon,
                    "affected_radius_km": 20.0,
                    "detected_at": datetime.utcnow()
                }

        # 2. Volume de Chuva Real (Sem simulação de nuvens)
        # Só alerta se tiver volume de água caindo (> 0mm)
        if "current" in weather_data:
            curr = weather_data["current"]
            has_rain_vol = "rain" in curr and curr["rain"] and curr["rain"].get("1h", 0) > 0.5 # Mais de 0.5mm/h
            
            if has_rain_vol:
                return {
                    "id": int(datetime.utcnow().timestamp()) + hash(context_id),
                    "event_type": "Chuva Detectada",
                    "severity": "Moderate",
                    "description": f"Volume: {curr['rain']['1h']}mm/h",
                    "affected_lat": lat,
                    "affected_lon": lon,
                    "affected_radius_km": 10.0,
                    "detected_at": datetime.utcnow()
                }

        return None

    @staticmethod
    async def analyze_active_journeys(db: AsyncSession):
        stmt = (
            select(Journey)
            .options(selectinload(Journey.vehicle))
            .where(Journey.is_active == True, Journey.end_time == None)
        )
        result = await db.execute(stmt)
        journeys = result.scalars().all()
        
        detected_events = []

        for journey in journeys:
            vehicle = journey.vehicle
            # SÓ PROCESSA SE TIVER GPS REAL
            if vehicle.last_latitude and vehicle.last_longitude:
                event = await WeatherIntelligenceService.analyze_location(
                    vehicle.last_latitude, 
                    vehicle.last_longitude, 
                    f"Veículo {vehicle.license_plate}"
                )
                if event:
                    detected_events.append(event)
                
        return detected_events