from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

from app.models.document_model import DocumentType


class DocumentBase(BaseModel):
    document_type: DocumentType
    expiry_date: date
    notes: Optional[str] = None


class DocumentCreate(DocumentBase):
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

    @validator('driver_id', always=True)
    def validate_owner(cls, v, values):
        if values.get('vehicle_id') is None and v is None:
            raise ValueError('Um documento deve ser associado a um veículo ou a um motorista.')
        if values.get('vehicle_id') is not None and v is not None:
            raise ValueError('Um documento não pode ser associado a um veículo e a um motorista ao mesmo tempo.')
        return v


class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class DocumentPublic(DocumentBase):
    id: int
    file_url: str
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

    owner_info: Optional[str] = None

    class Config:
        from_attributes = True
