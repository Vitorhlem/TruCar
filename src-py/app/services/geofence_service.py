from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shapely.geometry import Point, Polygon
from app.models.geofence_model import Geofence
from app.models.alert_model import Alert
from datetime import datetime

class GeofenceService:

    @staticmethod
    async def check_geofences(db: AsyncSession, vehicle_id: int, lat: float, lon: float):
        """
        Verifica se a coordenada atual está dentro de alguma cerca ativa.
        Gera alertas se necessário.
        """
        # 1. Busca todas as cercas ativas
        result = await db.execute(select(Geofence).where(Geofence.is_active == True))
        geofences = result.scalars().all()
        
        current_point = Point(lat, lon)
        triggered_alerts = []

        for zone in geofences:
            # Converte lista de pontos JSON para Polígono Shapely
            # polygon_points deve ser [[lat, lon], ...]
            if not zone.polygon_points or len(zone.polygon_points) < 3:
                continue
                
            poly = Polygon(zone.polygon_points)
            
            is_inside = poly.contains(current_point)
            
            # LÓGICA DE ALERTA:
            # Aqui você define a regra. Exemplo simples:
            # Se for RISK_ZONE e estiver DENTRO -> ALERTA
            if zone.type == "RISK_ZONE" and is_inside:
                alert = Alert(
                    vehicle_id=vehicle_id,
                    type="GEOFENCE_RISK",
                    severity="High",
                    description=f"Veículo entrou em Zona de Risco: {zone.name}",
                    latitude=lat,
                    longitude=lon,
                    created_at=datetime.utcnow(),
                    is_active=True
                )
                db.add(alert)
                triggered_alerts.append(f"Entrou em {zone.name}")
                
            # Se for SAFE_ZONE (Garagem) e estiver FORA -> ALERTA (opcional, ex: roubo noturno)
            # Para isso precisaríamos saber o estado anterior, o que exige mais lógica.
            # Por enquanto vamos focar na Zona de Risco.

        return triggered_alerts