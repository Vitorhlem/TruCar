import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .user_model import User
from .vehicle_model import Vehicle

# --- ENUM CORRIGIDO ---
# Os valores agora são strings em maiúsculas, exatamente como no frontend,
# o que resolve o erro de validação 422.
class MaintenanceStatus(str, enum.Enum):
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"
    EM_ANDAMENTO = "EM ANDAMENTO"
    CONCLUIDA = "CONCLUIDA"

class MaintenanceCategory(str, enum.Enum):
    # ... (sem alterações aqui)
    MECHANICAL = "Mecânica"
    ELECTRICAL = "Elétrica"
    BODYWORK = "Funilaria"
    OTHER = "Outro"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"
    id = Column(Integer, primary_key=True, index=True)
    problem_description = Column(Text, nullable=False)
    # --- COLUNA ATUALIZADA ---
    # Usando o SAEnum para garantir a consistência com a base de dados
    status = Column(SAEnum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.PENDENTE)
    category = Column(SAEnum(MaintenanceCategory), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # ... (o resto do modelo permanece igual) ...
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    manager_notes = Column(Text, nullable=True)
    reported_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    reporter = relationship("User", foreign_keys=[reported_by_id], back_populates="reported_requests")
    approver = relationship("User", foreign_keys=[approved_by_id])
    vehicle = relationship("Vehicle", back_populates="maintenance_requests")
    comments = relationship("MaintenanceComment", back_populates="request", cascade="all, delete-orphan")

class MaintenanceComment(Base):
    # ... (sem alterações aqui)
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