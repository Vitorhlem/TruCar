from pydantic import BaseModel
from app.models.alert_model import AlertLevel, AlertType
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    message: str
    level: AlertLevel
    organization_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    
    # CORREÇÃO: O nome no banco é 'timestamp', então usamos 'timestamp' aqui também.
    timestamp: Optional[datetime] = None
    
    # CORREÇÃO: Usar o Enum correto e valor padrão GENERIC
    type: AlertType = AlertType.GENERIC

    # NOTA: Removi 'date', 'is_active' e 'read' porque eles NÃO constavam 
    # no seu 'class Alert(Base)' enviado anteriormente. 
    # Se você tentar passar campos que não existem no banco, dará erro 422/500.