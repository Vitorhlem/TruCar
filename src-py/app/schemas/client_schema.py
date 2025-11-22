from pydantic import BaseModel, field_validator
from typing import Optional

class ClientBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    # CORREÇÃO: Alterado de EmailStr para str para evitar erro 500 com emails inválidos/vazios no banco
    email: Optional[str] = None
    
    # Campos de Endereço
    cep: Optional[str] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None

    # Validador: Se vier string vazia "", converte para None
    @field_validator('email', 'phone', 'contact_person', 'cep', mode='before')
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    cep: Optional[str] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None

    @field_validator('email', 'phone', 'contact_person', 'cep', mode='before')
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

class ClientPublic(ClientBase):
    id: int
    # organization_id: int # Opcional expor
    
    model_config = { "from_attributes": True }