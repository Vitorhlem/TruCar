import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum, DateTime)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base
from app.core.config import settings

if TYPE_CHECKING:
    from .inventory_transaction_model import InventoryTransaction
    from .fine_model import Fine
    from .freight_order_model import FreightOrder
    from .journey_model import Journey
    from .maintenance_model import MaintenanceRequest
    from .alert_model import Alert
    from .achievement_model import UserAchievement
    from .document_model import Document
    from .fuel_log_model import FuelLog
    from .organization_model import Organization

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False, default=generate_employee_id)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    notify_in_app: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    notify_by_email: Mapped[bool] = mapped_column(Boolean(), default=True, nullable=False)
    notification_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    reset_password_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    reset_password_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")

    inventory_transactions_performed: Mapped[List["InventoryTransaction"]] = relationship(
        "InventoryTransaction",
        foreign_keys="[InventoryTransaction.user_id]",
        back_populates="user"
    )

    inventory_transactions_received: Mapped[List["InventoryTransaction"]] = relationship(
        "InventoryTransaction",
        foreign_keys="[InventoryTransaction.related_user_id]",
        back_populates="related_user"
    )

    freight_orders: Mapped[List["FreightOrder"]] = relationship("FreightOrder", back_populates="driver")
    journeys: Mapped[List["Journey"]] = relationship("Journey", back_populates="driver", cascade="all, delete-orphan")
    reported_requests: Mapped[List["MaintenanceRequest"]] = relationship(
        "MaintenanceRequest", 
        foreign_keys="[MaintenanceRequest.reported_by_id]", 
        back_populates="reporter"
    )
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="driver")
    achievements: Mapped[List["UserAchievement"]] = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="driver", cascade="all, delete-orphan")
    fuel_logs: Mapped[List["FuelLog"]] = relationship("FuelLog", back_populates="user", cascade="all, delete-orphan")
    fines: Mapped[List["Fine"]] = relationship("Fine", back_populates="driver", cascade="all, delete-orphan")
    
    @property
    def is_superuser(self) -> bool:
        return self.email in settings.SUPERUSER_EMAILS