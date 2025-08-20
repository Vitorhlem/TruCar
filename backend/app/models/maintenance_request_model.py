from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

class MaintenanceComment(Base):
    __tablename__ = "maintenance_comments"
    
    id = Column(Integer, primary_key=True)
    comment_text = Column(Text, nullable=False)
    file_url = Column(String(512), nullable=True) # Campo para o link do anexo
    
    request_id = Column(Integer, ForeignKey("maintenance_requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("MaintenanceRequest", back_populates="comments")
    user = relationship("User")

class MaintenanceStatus(str, enum.Enum):
    PENDING = "Pendente"
    APPROVED = "Aprovada"
    REJECTED = "Rejeitada"
    IN_PROGRESS = "Em Andamento"
    COMPLETED = "Concluída"

class MaintenanceCategory(str, enum.Enum):
    MECHANICAL = "Mecânica"
    ELECTRICAL = "Elétrica"
    BODYWORK = "Funilaria"
    OTHER = "Outros"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    problem_description = Column(Text, nullable=False)
    status = Column(Enum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.PENDING)
    category = Column(Enum(MaintenanceCategory), nullable=False)
    
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    
    manager_notes = Column(Text, nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    reporter = relationship("User", foreign_keys=[reported_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    vehicle = relationship("Vehicle")
    comments = relationship("MaintenanceComment", back_populates="request", cascade="all, delete-orphan")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
