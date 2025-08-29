# ARQUIVO: backend/app/models/freight_order_model.py

import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class FreightStatus(str, enum.Enum):
    PENDING = "Pendente"
    IN_TRANSIT = "Em Trânsito"
    DELIVERED = "Entregue"
    CANCELED = "Cancelado"

class FreightOrder(Base):
    __tablename__ = "freight_orders"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(500), nullable=True)
    status = Column(Enum(FreightStatus), nullable=False, default=FreightStatus.PENDING)

    scheduled_start_time = Column(DateTime, nullable=True)
    scheduled_end_time = Column(DateTime, nullable=True)
    
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relacionamentos
    client = relationship("Client", back_populates="freight_orders")
    vehicle = relationship("Vehicle", back_populates="freight_orders")
    driver = relationship("User", back_populates="freight_orders")
    organization = relationship("Organization", back_populates="freight_orders")

    # A Ordem de Frete tem uma lista de Paradas
    stop_points = relationship("StopPoint", back_populates="freight_order", cascade="all, delete-orphan", order_by="StopPoint.sequence_order")
    
    # A Ordem de Frete pode ter várias Viagens (trechos) associadas
    journeys = relationship("Journey", back_populates="freight_order")