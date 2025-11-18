from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app import crud, deps
from app.schemas.telemetry_schema import TelemetryPayload

router = APIRouter()

@router.post("/traccar", status_code=status.HTTP_200_OK)
@router.get("/traccar", status_code=status.HTTP_200_OK)
async def receive_traccar_position(
    db: AsyncSession = Depends(deps.get_db),
    # Parâmetros enviados pelo App Traccar Client (Protocolo OsmAnd)
    id: str = Query(..., description="Device Identifier (IMEI ou ID único)"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    timestamp: Optional[int] = Query(None, description="Unix Timestamp"),
    speed: Optional[float] = Query(0.0, description="Speed in knots"),
    bearing: Optional[float] = Query(0.0, description="Direction/Heading"),
    altitude: Optional[float] = Query(0.0, description="Altitude"),
    accuracy: Optional[float] = Query(0.0, description="Accuracy"),
    batt: Optional[float] = Query(None, description="Battery Level")
):
    """
    Recebe dados de GPS diretamente do app Traccar Client.
    Suporta tanto GET quanto POST (formato OsmAnd).
    """
    
    # 1. Tratamento do Timestamp (O app envia em segundos ou milissegundos)
    if timestamp:
        try:
            # Se for muito grande (ex: 1600000000000), é milissegundos
            if timestamp > 1000000000000:
                dt_timestamp = datetime.fromtimestamp(timestamp / 1000.0)
            else:
                dt_timestamp = datetime.fromtimestamp(timestamp)
        except:
            dt_timestamp = datetime.utcnow()
    else:
        dt_timestamp = datetime.utcnow()

    # 2. Conversão de Velocidade (Nós para Km/h se necessário, mas aqui salvamos cru)
    # Opcional: Traccar envia em 'nós' (knots). 1 knot = 1.852 km/h.
    speed_kmh = speed * 1.852 if speed else 0.0

    # 3. Cria o Objeto de Telemetria do TruCar
    telemetry_data = TelemetryPayload(
        device_id=id,
        timestamp=dt_timestamp,
        latitude=lat,
        longitude=lon,
        engine_hours=0, # O app celular não lê horímetro
        fuel_level=batt, # Podemos usar o nível de bateria do celular como "combustível" para monitorar
        error_codes=[]
    )

    # 4. Atualiza o Veículo no Banco de Dados
    # Essa função (que já existe no seu crud_vehicle.py) busca pelo 'telemetry_device_id'
    vehicle = await crud.vehicle.update_vehicle_from_telemetry(db=db, payload=telemetry_data)

    if not vehicle:
        print(f"⚠️ [Integração Traccar] Recebido ID '{id}' mas nenhum veículo encontrado com esse Device ID.")
    else:
        print(f"✅ [Integração Traccar] Veículo {vehicle.license_plate} atualizado! Lat: {lat}, Lon: {lon}")
    
    # Retorna sucesso para o App não ficar tentando reenviar
    return "OK"