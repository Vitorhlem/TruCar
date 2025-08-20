from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReportRequest(BaseModel):
    report_type: str # Ex: "cost_by_vehicle", "activity_by_driver"
    date_from: date
    date_to: date
    target_id: int # ID do veículo ou do motorista