import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Enum as SAEnum, Boolean # <-- 1. IMPORTAR BOOLEAN
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional 

from app.db.base_class import Base
from .user_model import User
from .vehicle_model import Vehicle
from .vehicle_component_model import VehicleComponent 

class MaintenanceStatus(str, enum.Enum):
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"
    EM_ANDAMENTO = "EM ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"

class MaintenanceCategory(str, enum.Enum):
    MECHANICAL = "Mecânica"
    ELECTRICAL = "Elétrica"
    BODYWORK = "Funilaria"
    OTHER = "Outro"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    problem_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[MaintenanceStatus] = mapped_column(SAEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.PENDENTE)
    category: Mapped[MaintenanceCategory] = mapped_column(SAEnum(MaintenanceCategory), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    manager_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    reported_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)

    reporter: Mapped[Optional["User"]] = relationship("User", foreign_keys=[reported_by_id], back_populates="reported_requests")
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by_id])
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="maintenance_requests")
    comments: Mapped[List["MaintenanceComment"]] = relationship("MaintenanceComment", back_populates="request", cascade="all, delete-orphan")

    part_changes: Mapped[List["MaintenancePartChange"]] = relationship(
        "MaintenancePartChange", 
        back_populates="maintenance_request", 
        cascade="all, delete-orphan"
    )

class MaintenanceComment(Base):
    __tablename__ = "maintenance_comments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("maintenance_requests.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    request: Mapped["MaintenanceRequest"] = relationship("MaintenanceRequest", back_populates="comments")
    user: Mapped[Optional["User"]] = relationship("User")


class MaintenancePartChange(Base):
    """
    Rastreia a substituição de um componente (DE-PARA)
    dentro de um chamado de manutenção.
    """
    __tablename__ = "maintenance_part_changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    maintenance_request_id: Mapped[int] = mapped_column(Integer, ForeignKey("maintenance_requests.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    component_removed_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle_components.id"))
    component_installed_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle_components.id"))

    # --- CAMPO NOVO (BÔNUS) ---
    is_reverted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    # --- FIM DA ADIÇÃO ---

    maintenance_request: Mapped["MaintenanceRequest"] = relationship("MaintenanceRequest", back_populates="part_changes")
    user: Mapped["User"] = relationship("User")
    
    component_removed: Mapped["VehicleComponent"] = relationship(
        "VehicleComponent", 
        foreign_keys=[component_removed_id]
    )
    component_installed: Mapped["VehicleComponent"] = relationship(
        "VehicleComponent", 
        foreign_keys=[component_installed_id]
    )