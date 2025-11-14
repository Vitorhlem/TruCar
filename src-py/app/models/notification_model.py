from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

# --- NOVO ENUM ADICIONADO ---
class NotificationType(str, enum.Enum):
    # Alertas Críticos
    MAINTENANCE_DUE_DATE = "maintenance_due_date"
    MAINTENANCE_DUE_KM = "maintenance_due_km"
    DOCUMENT_EXPIRING = "document_expiring"
    LOW_STOCK = "low_stock"
    TIRE_STATUS_BAD = "tire_status_bad"
    ABNORMAL_FUEL_CONSUMPTION = "abnormal_fuel_consumption"
    COST_EXCEEDED = "cost_exceeded"
    NEW_FINE_REGISTERED = "new_fine_registered"
    FINE_PAYMENT_DUE = "fine_payment_due"
    
    # Notificações Operacionais
    FREIGHT_ASSIGNED = "freight_assigned"
    FREIGHT_UPDATED = "freight_updated"
    MAINTENANCE_REQUEST_NEW = "maintenance_request_new"
    MAINTENANCE_REQUEST_STATUS_UPDATE = "maintenance_request_status_update"
    MAINTENANCE_REQUEST_NEW_COMMENT = "maintenance_request_new_comment"
    JOURNEY_STARTED = "journey_started"
    JOURNEY_ENDED = "journey_ended"
    
    # Gamificação
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    LEADERBOARD_TOP3 = "leaderboard_top3"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Para qual usuário é o alerta
    
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # --- CAMPOS ATUALIZADOS/ADICIONADOS ---
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    
    # Link genérico para qualquer outra tabela (multa, documento, manutenção, etc.)
    related_entity_type = Column(String, nullable=True) # ex: "fine", "document", "maintenance_request"
    related_entity_id = Column(Integer, nullable=True)

    # Mantemos o link de veículo para conveniência e retrocompatibilidade
    related_vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True)
    # --- FIM DAS MUDANÇAS ---

    user = relationship("User")
    vehicle = relationship("Vehicle")
    organization = relationship("Organization")