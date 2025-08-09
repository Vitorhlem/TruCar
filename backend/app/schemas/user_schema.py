from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.user_model import UserRole

# --- Schemas Base ---
# Contém os campos comuns a vários outros schemas para evitar repetição (DRY).

class UserBase(BaseModel):
    """Schema base para usuários, com campos compartilhados."""
    email: EmailStr
    full_name: str

# --- Schemas para Operações Específicas ---

class UserCreate(UserBase):
    """Schema usado para criar um novo usuário."""
    password: str
    role: UserRole = UserRole.DRIVER

class UserUpdate(BaseModel):
    """Schema usado para atualizar um usuário. Todos os campos são opcionais."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


# --- Schemas para Respostas da API ---
# Estes schemas definem os dados que são enviados de volta ao cliente.
# É uma prática de segurança crucial, pois omitimos campos sensíveis como a senha.

class UserPublic(UserBase):
    """
    Schema público do usuário, retornado pela API.
    Seguro para ser exposto, não contém a senha.
    """
    id: int
    role: UserRole
    is_active: bool
    
    # Configuração para permitir que o Pydantic leia os dados
    # diretamente de um modelo SQLAlchemy (ORM).
    model_config = {
        "from_attributes": True
    }