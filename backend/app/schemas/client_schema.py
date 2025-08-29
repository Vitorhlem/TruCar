# ARQUIVO: backend/app/schemas/client_schema.py

from pydantic import BaseModel, EmailStr
from typing import Optional

class ClientBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class ClientPublic(ClientBase):
    id: int
    
    model_config = { "from_attributes": True }