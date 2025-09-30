from pydantic import BaseModel
from datetime import datetime
from .part_schema import PartPublic

class VehicleComponentBase(BaseModel):
    part_id: int
    quantity: int # Usado apenas na criação

class VehicleComponentCreate(VehicleComponentBase):
    pass

class VehicleComponentPublic(BaseModel):
    id: int
    installation_date: datetime
    uninstallation_date: datetime | None
    is_active: bool
    part: PartPublic

    class Config:
        from_attributes = True