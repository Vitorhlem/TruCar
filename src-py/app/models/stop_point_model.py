
import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class StopPointType(str, enum.Enum):
    PICKUP = "Coleta"
    DELIVERY = "Entrega"

class StopPointStatus(str, enum.Enum):
    PENDING = "Pendente"
    COMPLETED = "Concluído"

class StopPoint(Base):
    __tablename__ = "stop_points"
    
    id = Column(Integer, primary_key=True, index=True)
    
    freight_order_id = Column(Integer, ForeignKey("freight_orders.id"), nullable=False)
    sequence_order = Column(Integer, nullable=False)
    type = Column(Enum(StopPointType), nullable=False)
    status = Column(Enum(StopPointStatus), nullable=False, default=StopPointStatus.PENDING)
    
    address = Column(String(500), nullable=False)
    cargo_description = Column(String(500), nullable=True)
    
    scheduled_time = Column(DateTime, nullable=False)
    actual_arrival_time = Column(DateTime, nullable=True)
    
    freight_order = relationship("FreightOrder", back_populates="stop_points")