import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.core.config import settings

def generate_employee_id():
    """Gera um ID de funcionário único e legível, ex: TRC-a1b2c3d4"""
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
    
    employee_id = Column(String(50), unique=True, index=True, nullable=False, default=generate_employee_id)

    role = Column(SAEnum(UserRole), nullable=False)
    is_active = Column(Boolean(), default=True)
    avatar_url = Column(String(512), nullable=True)
    
    notify_in_app = Column(Boolean(), default=True, nullable=False)
    notify_by_email = Column(Boolean(), default=True, nullable=False)
    notification_email = Column(String(100), nullable=True)
    
    reset_password_token = Column(String(255), nullable=True, index=True)
    reset_password_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")

    # --- CORREÇÃO ADICIONADA AQUI ---
    # Adicionamos as relações inversas para resolver a ambiguidade.
    # Dizemos ao SQLAlchemy qual ForeignKey usar para cada relação.
    
    # Transações que este utilizador realizou
    inventory_transactions_performed = relationship(
        "InventoryTransaction",
        foreign_keys="[InventoryTransaction.user_id]",
        back_populates="user"
    )

    inventory_transactions_received = relationship(
        "InventoryTransaction",
        foreign_keys="[InventoryTransaction.related_user_id]",
        back_populates="related_user"
    )

    # Transações onde este utilizador recebeu um item (ex: um motorista)
    inventory_transactions_received = relationship(
        "InventoryTransaction",
        foreign_keys="[InventoryTransaction.related_user_id]",
        back_populates="related_user",
        cascade="all, delete-orphan"
    )
    # --- FIM DA CORREÇÃO ---


    @property
    def is_superuser(self) -> bool:
        return self.email in settings.SUPERUSER_EMAILS

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