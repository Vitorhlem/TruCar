import enum
import uuid # Importa a biblioteca para gerar IDs únicos
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.core.config import settings

def generate_employee_id():
    """Gera um ID de funcionário único e legível, ex: TRC-a1b2c3d4"""
    # Usamos os primeiros 8 caracteres de um UUID para garantir unicidade
    unique_part = uuid.uuid4().hex[:8]
    return f"TRC-{unique_part}"

class UserRole(str, enum.Enum):
    CLIENTE_ATIVO = "cliente_ativo"
    CLIENTE_DEMO = "cliente_demo"
    DRIVER = "driver"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # --- CAMPO ATUALIZADO PARA GERAÇÃO AUTOMÁTICA ---
    # O `default=generate_employee_id` garante que o campo seja preenchido automaticamente.
    # `nullable=False` garante que todo usuário terá um ID.
    employee_id = Column(String(50), unique=True, index=True, nullable=False, default=generate_employee_id)
    # --- FIM DA ALTERAÇÃO ---

    role = Column(SAEnum(UserRole), nullable=False)
    is_active = Column(Boolean(), default=True)
    avatar_url = Column(String(512), nullable=True)
    
    notify_in_app = Column(Boolean(), default=True, nullable=False)
    notify_by_email = Column(Boolean(), default=True, nullable=False)
    notification_email = Column(String(100), nullable=True)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")

    @property
    def is_superuser(self) -> bool:
        return self.email in settings.SUPERUSER_EMAILS

    # Relações existentes
    freight_orders = relationship("FreightOrder", back_populates="driver")
    journeys = relationship("Journey", back_populates="driver", cascade="all, delete-orphan")
    reported_requests = relationship(
        "MaintenanceRequest", 
        foreign_keys="MaintenanceRequest.reported_by_id", 
        back_populates="reporter"
    )
    alerts = relationship("Alert", back_populates="driver")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="driver", cascade="all, delete-orphan")
    fuel_logs = relationship("FuelLog", back_populates="user", cascade="all, delete-orphan")


