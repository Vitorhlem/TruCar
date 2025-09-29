from pydantic import BaseModel
from typing import Optional

class PartBase(BaseModel):
    name: str
    category: str
    part_number: Optional[str] = None
    brand: Optional[str] = None
    stock: int
    min_stock: int
    location: Optional[str] = None
    notes: Optional[str] = None
    # O campo photo_url foi removido daqui, pois é gerado pelo servidor.

class PartCreate(PartBase):
    pass

class PartUpdate(PartBase):
    pass

class PartPublic(PartBase):
    id: int
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True

