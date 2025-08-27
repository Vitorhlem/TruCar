import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base
# REMOVEMOS O IMPORT QUE CAUSAVA O CICLO:
# from .maintenance_model import MaintenanceRequest 

class UserRole(str, enum.Enum):
    MANAGER = "manager"
    DRIVER = "driver"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean(), default=True)
    avatar_url = Column(String(512), nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")

    # Relações com outras tabelas
    journeys = relationship("Journey", back_populates="driver", cascade="all, delete-orphan")
    
    # A CORREÇÃO CRUCIAL: Usamos uma string para referenciar a chave estrangeira
    reported_requests = relationship(
        "MaintenanceRequest", 
        foreign_keys="MaintenanceRequest.reported_by_id", 
        back_populates="reporter"
    )