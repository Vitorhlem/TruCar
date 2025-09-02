from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Nota: Estes não são modelos de base de dados (SQLAlchemy),
# são "schemas" Pydantic para definir a estrutura da resposta da API.

class KmPerDay(BaseModel):
    date: date
    total_km: float

class UpcomingMaintenance(BaseModel):
    vehicle_info: str
    due_date: Optional[date] = None
    due_km: Optional[float] = None

    class Config:
        from_attributes = True
