from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Importa outros schemas que são usados nas respostas
from .user_schema import UserPublic
from .vehicle_schema import VehiclePublic
# --- NOVO IMPORT ---
# Importamos o Enum do nosso model para reutilizá-lo
from app.models.fuel_log_model import VerificationStatus


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

# Schema usado para atualizar um registo.
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
    vehicle: VehiclePublic

    # --- NOVOS CAMPOS PARA INTEGRAÇÃO ---
    verification_status: VerificationStatus
    provider_name: Optional[str] = None
    gas_station_name: Optional[str] = None
    # --- FIM DA ADIÇÃO ---
    
    model_config = { "from_attributes": True }


# --- NOVO SCHEMA PARA O SIMULADOR DE INTEGRAÇÃO ---
class FuelProviderTransaction(BaseModel):
    transaction_id: str
    vehicle_license_plate: str
    driver_cpf: str # Usaremos um identificador do motorista
    timestamp: datetime
    liters: float
    total_cost: float
    gas_station_name: str
    gas_station_latitude: float
    gas_station_longitude: float

