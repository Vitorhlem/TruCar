
from pydantic import BaseModel, constr
from typing import Optional, List
from datetime import date
from app.models.vehicle_model import VehicleStatus

LicensePlateStr = constr(strip_whitespace=True, to_upper=True)

class VehicleBase(BaseModel):
    brand: str
    model: str
    year: int
    photo_url: Optional[str] = None
    current_km: Optional[int] = 0
    current_engine_hours: Optional[float] = 0
    next_maintenance_date: Optional[date] = None
    next_maintenance_km: Optional[int] = None
    maintenance_notes: Optional[str] = None
    identifier: Optional[str] = None
    license_plate: Optional[LicensePlateStr] = None
    telemetry_device_id: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    photo_url: Optional[str] = None
    status: Optional[VehicleStatus] = None
    current_km: Optional[int] = None
    current_engine_hours: Optional[float] = None
    next_maintenance_date: Optional[date] = None
    next_maintenance_km: Optional[int] = None
    maintenance_notes: Optional[str] = None
    telemetry_device_id: Optional[str] = None

class VehiclePublic(VehicleBase):
    id: int
    status: VehicleStatus
    last_latitude: Optional[float] = None   # Adicionado para o mapa
    last_longitude: Optional[float] = None  # Adicionado para o mapa
    
    model_config = { "from_attributes": True }

class VehicleListResponse(BaseModel):
    vehicles: List[VehiclePublic]
    total_items: int