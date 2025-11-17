import enum
from typing import TYPE_CHECKING, Optional
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum, Float, Date, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base

if TYPE_CHECKING:
    from .user_model import User
    from .vehicle_model import Vehicle
    from .organization_model import Organization
    from .vehicle_cost_model import VehicleCost  # <-- Importar o Custo

class FineStatus(str, enum.Enum):
    PENDING = "Pendente"
    PAID = "Paga"
    APPEALED = "Em Recurso"
    CANCELED = "Cancelada"

class Fine(Base):
    __tablename__ = "fines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    infraction_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[FineStatus] = mapped_column(SAEnum(FineStatus), nullable=False, default=FineStatus.PENDING)
    
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    organization: Mapped["Organization"] = relationship("Organization")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="fines")
    driver: Mapped[Optional["User"]] = relationship("User", back_populates="fines")
    
    cost: Mapped[Optional["VehicleCost"]] = relationship(
        "VehicleCost",
        back_populates="fine",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin"  # Carrega o custo junto com a multa
    )