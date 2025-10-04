from pydantic import BaseModel
from typing import Optional

class PartBase(BaseModel):
    name: str
    category: str
    serial_number: Optional[str] = None
    part_number: Optional[str] = None
    brand: Optional[str] = None
    stock: int
    min_stock: int
    location: Optional[str] = None
    notes: Optional[str] = None
    value: Optional[float] = None
    lifespan_km: Optional[int] = None

class PartCreate(PartBase):
    pass

class PartUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    serial_number: Optional[str] = None
    part_number: Optional[str] = None
    brand: Optional[str] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    value: Optional[float] = None
    lifespan_km: Optional[int] = None

class Part(PartBase):
    id: int
    photo_url: Optional[str] = None
    invoice_url: Optional[str] = None

    class Config:
        from_attributes = True

class PartPublic(Part):
    pass