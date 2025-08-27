# backend/app/models/maintenance_model.py

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .user_model import User
from .vehicle_model import Vehicle

# Enums do Python para definir as opções possíveis
class MaintenanceStatus(str, enum.Enum):
    PENDING = "Pendente"
    APPROVED = "Aprovado"
    REJECTED = "Rejeitado"
    IN_PROGRESS = "Em Progresso"
    COMPLETED = "Concluído"

class MaintenanceCategory(str, enum.Enum):
    MECHANICAL = "Mecânica"
    ELECTRICAL = "Elétrica"
    BODYWORK = "Funilaria"
    OTHER = "Outro"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    problem_description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default=MaintenanceStatus.PENDING.value)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    manager_notes = Column(Text, nullable=True)

    # Chaves Estrangeiras
    reported_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Relacionamentos
    reporter = relationship("User", foreign_keys=[reported_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    vehicle = relationship("Vehicle", back_populates="maintenance_requests")
    comments = relationship("MaintenanceComment", back_populates="request", cascade="all, delete-orphan")

class MaintenanceComment(Base):
    __tablename__ = "maintenance_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_text = Column(Text, nullable=False)
    file_url = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("maintenance_requests.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    request = relationship("MaintenanceRequest", back_populates="comments")
    user = relationship("User")