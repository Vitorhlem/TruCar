
from pydantic import BaseModel, Field
from app.models.implement_model import ImplementStatus
from typing import Optional
from datetime import date

class ImplementBase(BaseModel):
    name: str
    brand: str
    model: str
    year: int
    identifier: Optional[str] = None
    status: str = Field(default=ImplementStatus.AVAILABLE)
    
    type: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_value: Optional[float] = None
    notes: Optional[str] = None


class ImplementCreate(ImplementBase):
    pass

class ImplementUpdate(ImplementBase):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    status: Optional[str] = None
    
    type: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_value: Optional[float] = None
    notes: Optional[str] = None


class ImplementPublic(ImplementBase):
    id: int
    
    
    model_config = { "from_attributes": True }