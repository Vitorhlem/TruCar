# backend/app/schemas/fuel_log_schema.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Importa outros schemas que são usados nas respostas
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic

# Schema base com os campos comuns que são sempre necessários
class FuelLogBase(BaseModel):
    odometer: int
    liters: float
    total_cost: float
    vehicle_id: int
    receipt_photo_url: Optional[str] = None

# Schema usado para criar um novo registo de abastecimento
class FuelLogCreate(FuelLogBase):
    pass

# O SCHEMA QUE ESTAVA EM FALTA:
# Usado para atualizar um registo. Todos os campos são opcionais.
class FuelLogUpdate(BaseModel):
    odometer: Optional[int] = None
    liters: Optional[float] = None
    total_cost: Optional[float] = None
    vehicle_id: Optional[int] = None
    receipt_photo_url: Optional[str] = None

# Schema para as respostas da API (o que é enviado para o front-end)
class FuelLogPublic(FuelLogBase):
    id: int
    timestamp: datetime
    user: UserPublic
    vehicle: VehiclePublic # Para mostrar os detalhes do veículo na resposta
    
    model_config = { "from_attributes": True }