import httpx
import polyline
from shapely.geometry import LineString, Point
from app.services.weather_intelligence import WeatherIntelligenceService

class RouteService:
    OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

    @staticmethod
    async def get_optimized_route(start_lat, start_lon, dest_lat, dest_lon, db_session):
        # --- LÓGICA DE FALLBACK (Visualização) ---
        # Se o veículo não tiver GPS (0 ou None), usamos SP para você poder testar a rota.
        # Isso não altera o banco de dados, é apenas para o cálculo matemático deste momento.
        if not start_lat or not start_lon or (start_lat == 0 and start_lon == 0):
            start_lat, start_lon = -23.5505, -46.6333
        # -----------------------------------------

        # 1. Rota Padrão (OSRM)
        route_data = await RouteService._fetch_osrm_route(start_lat, start_lon, dest_lat, dest_lon)
        if not route_data or 'routes' not in route_data:
            return None

        geometry_code = route_data['routes'][0]['geometry']
        decoded_points = polyline.decode(geometry_code)
        route_line = LineString(decoded_points)
        
        # 2. Scanner de Rota (Weather Intelligence Real)
        # Analisa o clima em 5 pontos da rota para garantir que detecta chuvas no caminho
        risks = []
        total_points = len(decoded_points)
        
        # Define pontos de checagem (Início, 25%, 50%, 75%, Fim)
        indices_to_check = [0, total_points - 1]
        if total_points > 5:
            indices_to_check = [
                0, 
                total_points // 4, 
                total_points // 2, 
                (total_points * 3) // 4, 
                total_points - 1
            ]

        for idx in indices_to_check:
            pt = decoded_points[idx]
            # Chama a inteligência APENAS com dados reais da API
            risk = await WeatherIntelligenceService.analyze_location(pt[0], pt[1], f"Rota Pt {idx}")
            if risk:
                risks.append(risk)
                if risk['severity'] == 'Severe': # Se achar perigo grave, para de buscar
                    break

        collision_event = None
        
        # 3. Verifica Colisão Geométrica
        for risk in risks:
            storm_point = Point(risk['affected_lat'], risk['affected_lon'])
            storm_radius_deg = (risk['affected_radius_km'] * 1000) / 111000.0 
            storm_circle = storm_point.buffer(storm_radius_deg)
            
            if route_line.intersects(storm_circle):
                collision_event = risk
                break 
        
        # 4. Cálculo de Desvio (Se necessário)
        if collision_event:
            # Cria um ponto de passagem (waypoint) fora da área de risco
            offset = (collision_event['affected_radius_km'] * 1000 / 111000.0) + 0.05
            avoid_lat = collision_event['affected_lat'] + offset
            avoid_lon = collision_event['affected_lon'] + offset
            
            evasive_route = await RouteService._fetch_osrm_route(
                start_lat, start_lon, dest_lat, dest_lon, 
                middle_lat=avoid_lat, middle_lon=avoid_lon
            )
            
            if evasive_route and 'routes' in evasive_route:
                final_points = polyline.decode(evasive_route['routes'][0]['geometry'])
                return {
                    "geometry_points": final_points,
                    "weather_alert": collision_event
                }

        # 5. Retorno Normal
        return {
            "geometry_points": decoded_points,
            "weather_alert": None
        }

    @staticmethod
    async def _fetch_osrm_route(start_lat, start_lon, end_lat, end_lon, middle_lat=None, middle_lon=None):
        coordinates = f"{start_lon},{start_lat}"
        if middle_lat:
            coordinates += f";{middle_lon},{middle_lat}"
        coordinates += f";{end_lon},{end_lat}"

        url = f"{RouteService.OSRM_BASE_URL}/{coordinates}?overview=full&geometries=polyline"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=10.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                print(f"Erro OSRM: {e}")
        return None