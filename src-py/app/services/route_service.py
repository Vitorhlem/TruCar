import httpx
import polyline
from shapely.geometry import LineString, Point
from app.services.weather_intelligence import WeatherIntelligenceService

class RouteService:
    OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

    @staticmethod
    async def get_optimized_route(start_lat, start_lon, dest_lat, dest_lon, db_session):
        # --- LÓGICA DE FALLBACK (Visualização) ---
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
        
        # 2. SCANNER DE ALTA PRECISÃO
        # Em vez de 5 pontos fixos, vamos escanear proporcionalmente ao tamanho da rota.
        # Limitamos a 20 amostras para não bloquear sua API Key (limite de requests),
        # mas isso cobre muito bem a maioria das viagens.
        
        total_points = len(decoded_points)
        risks = []
        
        # Define a quantidade de checagens (Mínimo 10, Máximo 25)
        num_samples = min(max(10, total_points // 50), 25) 
        step = max(1, total_points // num_samples)
        
        indices_to_check = list(range(0, total_points, step))
        
        # Garante que o destino final seja verificado
        if indices_to_check[-1] != total_points - 1:
            indices_to_check.append(total_points - 1)

        print(f"📡 SCANNER DE ROTA: Analisando {len(indices_to_check)} pontos estratégicos...")

        collision_event = None

        for i, idx in enumerate(indices_to_check):
            pt = decoded_points[idx]
            # Log para você ver no terminal onde ele está olhando
            print(f"   [{i+1}/{len(indices_to_check)}] Checando Lat: {pt[0]:.4f}, Lon: {pt[1]:.4f} ...")
            
            # Chama a inteligência
            risk = await WeatherIntelligenceService.analyze_location(pt[0], pt[1], f"Rota Pt {idx}")
            
            if risk:
                print(f"   ⚠️ ALERTA ENCONTRADO: {risk['event_type']} - {risk['description']}")
                risks.append(risk)
                
                # VERIFICAÇÃO GEOMÉTRICA IMEDIATA
                # Se achou clima ruim, verifica se realmente bloqueia a estrada
                storm_point = Point(risk['affected_lat'], risk['affected_lon'])
                # Raio de impacto (20km convertidos para graus aprox.)
                storm_radius_deg = (risk['affected_radius_km'] * 1000) / 111000.0 
                storm_circle = storm_point.buffer(storm_radius_deg)
                
                if route_line.intersects(storm_circle):
                    collision_event = risk
                    print("   ⛔ BLOQUEIO CONFIRMADO! Iniciando desvio...")
                    break # Para de procurar, já temos um motivo para desviar
        
        # 4. Cálculo de Desvio (Se necessário)
        if collision_event:
            # Cria um ponto de passagem (waypoint) fora da área de risco
            offset = (collision_event['affected_radius_km'] * 1000 / 111000.0) + 0.08 # +800m de margem
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
        print("✅ Rota limpa. Nenhuma ameaça crítica detectada.")
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