import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# --- ENUM DE PAPÉIS FINAL ---
class UserRole(str, enum.Enum):
    # Representa o "Cliente Ativo" com acesso total de gestor
    CLIENTE_ATIVO = "cliente_ativo"
    # Representa o "Cliente Demo" com acesso limitado de gestor
    CLIENTE_DEMO = "cliente_demo"
    # Papel para os motoristas da frota
    DRIVER = "driver"
# --- FIM DA ALTERAÇÃO ---


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False) # Usa o Enum final
    is_active = Column(Boolean(), default=True)
    avatar_url = Column(String(512), nullable=True)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")

    # Relações (permanecem as mesmas)
    freight_orders = relationship("FreightOrder", back_populates="driver")
    journeys = relationship("Journey", back_populates="driver", cascade="all, delete-orphan")
    reported_requests = relationship(
        "MaintenanceRequest", 
        foreign_keys="MaintenanceRequest.reported_by_id", 
        back_populates="reporter"
    )