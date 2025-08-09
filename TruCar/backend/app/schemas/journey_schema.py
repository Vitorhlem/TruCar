from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.journey_model import JourneyType
from app.schemas.user_schema import UserPublic
from app.schemas.vehicle_schema import VehiclePublic

# --- Schema Base ---

class JourneyBase(BaseModel):
    """Schema base para viagens, com os campos fornecidos no início."""
    vehicle_id: int
    start_mileage: int
    trip_type: JourneyType = JourneyType.SPECIFIC_DESTINATION
    destination_address: Optional[str] = None
    trip_description: Optional[str] = None

# --- Schemas para Operações Específicas ---

class JourneyCreate(JourneyBase):
    """Schema usado para criar (iniciar) uma nova viagem."""
    # O driver_id será pego do token de autenticação, não do corpo da requisição.
    pass

class JourneyUpdate(BaseModel):
    """Schema usado para finalizar uma viagem. Requer apenas a quilometragem final."""
    end_mileage: int


# --- Schema para Resposta da API ---

class JourneyPublic(JourneyBase):
    """
    Schema público completo da viagem, retornado pela API.
    Inclui detalhes do motorista e do veículo.
    """
    id: int
    is_active: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    end_mileage: Optional[int] = None
    
    # Schemas aninhados para uma resposta rica e completa
    driver: UserPublic
    vehicle: VehiclePublic
    
    model_config = {
        "from_attributes": True
    }