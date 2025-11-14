from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

# Importamos o Enum do nosso model para reutilizá-lo
from app.models.document_model import DocumentType


# Schema base com os campos comuns
class DocumentBase(BaseModel):
    document_type: DocumentType
    expiry_date: date
    notes: Optional[str] = None


# Schema para criar um novo documento
class DocumentCreate(DocumentBase):
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

    # Validador para garantir que o documento seja associado
    # a um veículo OU a um motorista, mas não a ambos (ou a nenhum).
    @validator('driver_id', always=True)
    def validate_owner(cls, v, values):
        if values.get('vehicle_id') is None and v is None:
            raise ValueError('Um documento deve ser associado a um veículo ou a um motorista.')
        if values.get('vehicle_id') is not None and v is not None:
            raise ValueError('Um documento não pode ser associado a um veículo e a um motorista ao mesmo tempo.')
        return v


# Schema para atualizar um documento existente (todos os campos são opcionais)
class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


# Schema para exibir os dados de um documento na resposta da API
class DocumentPublic(DocumentBase):
    id: int
    file_url: str
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None

    # Campo extra que será preenchido pela nossa lógica de negócio (CRUD)
    # para facilitar a exibição no frontend.
    owner_info: Optional[str] = None

    class Config:
        from_attributes = True
