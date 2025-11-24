from pydantic import BaseModel
from app.models.alert_model import AlertLevel
from typing import Optional

class AlertCreate(BaseModel):
    message: str
    level: AlertLevel
    organization_id: int
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None