from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, deps
from datetime import datetime
from pydantic import BaseModel
from app.schemas.alert_schema import AlertCreate
from app.models.alert_model import AlertLevel, AlertType

router = APIRouter()

# Schema para receber os dados brutos do script Python/YOLO
class DMSAlertPayload(BaseModel):
    truck_id: int
    event_type: str
    timestamp: datetime
    severity: str
    description: str

@router.post("/alert", status_code=201)
async def receive_dms_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_in: DMSAlertPayload,
):
    """
    Recebe alertas do TruCar.Sentinel (Edge AI) e salva no banco.
    """
    # 1. Buscar veículo
    vehicle = await crud.vehicle.get_by_id(db, id=alert_in.truck_id)
    if not vehicle:
        # Se não achar, loga e retorna 404
        print(f"❌ Veículo não encontrado para ID: {alert_in.truck_id}")
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # 2. Mapeamento de Severidade (String -> Enum)
    # O YOLO envia "HIGH", "MEDIUM", mas o banco aceita "CRITICAL", "WARNING"
    severity_map = {
        "HIGH": AlertLevel.CRITICAL,
        "CRITICAL": AlertLevel.CRITICAL,
        "MEDIUM": AlertLevel.WARNING,
        "WARNING": AlertLevel.WARNING,
        "LOW": AlertLevel.INFO,
        "INFO": AlertLevel.INFO
    }
    # Se vier algo desconhecido, define como INFO
    internal_level = severity_map.get(alert_in.severity.upper(), AlertLevel.INFO)

    # 3. Mapeamento de Tipo de Evento (String -> Enum)
    # Mapeia eventos externos para os tipos do seu sistema
    type_map = {
        "DISTRACTION_CELLPHONE": AlertType.GENERIC, # Ou mapeie para um tipo específico se tiver
        "SPEEDING": AlertType.SPEEDING,
        "ROAD_HAZARD": AlertType.ROAD_HAZARD
    }
    internal_type = type_map.get(alert_in.event_type, AlertType.GENERIC)

    try:
        # 4. Criar objeto AlertCreate
        # IMPORTANTE: Passamos 'timestamp' aqui, e não 'date'
        alert_create_data = AlertCreate(
            organization_id=vehicle.organization_id,
            vehicle_id=vehicle.id,
            level=internal_level,
            message=alert_in.description,
            timestamp=alert_in.timestamp, # 👈 Campo correto
            type=internal_type
        )

        # 5. Salvar no banco
        alert = await crud.alert.create(db=db, obj_in=alert_create_data)
        
        print(f"💾 ALERTA SALVO NO DB: ID {alert.id} - {alert.message}")
        return alert

    except Exception as e:
        print(f"❌ Erro ao processar alerta: {e}")
        # Retorna 422 com a mensagem do erro para facilitar o debug
        raise HTTPException(status_code=422, detail=f"Erro ao salvar alerta: {str(e)}")