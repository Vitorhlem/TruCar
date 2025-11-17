from pydantic import BaseModel
from datetime import datetime
from typing import Optional # Importar Optional
from .part_schema import PartPublic

from .inventory_transaction_schema import TransactionForComponent 

class VehicleComponentBase(BaseModel):
    part_id: int
    quantity: int 

class VehicleComponentCreate(VehicleComponentBase):
    pass

class VehicleComponentPublic(BaseModel):
    id: int
    installation_date: datetime
    uninstallation_date: datetime | None
    is_active: bool
    part: PartPublic

    inventory_transaction: Optional[TransactionForComponent] = None

    class Config:
        from_attributes = True