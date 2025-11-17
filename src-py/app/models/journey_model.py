from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Float
)
from sqlalchemy.orm import relationship
from .implement_model import Implement
from app.db.base_class import Base
from .organization_model import Organization
from .user_model import User
from app.schemas.journey_schema import JourneyType

class Journey(Base):
    __tablename__ = "journeys"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_mileage = Column(Integer, nullable=False)
    end_mileage = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    trip_type = Column(String(50), nullable=False)
    implement_id = Column(Integer, ForeignKey("implements.id"), nullable=True)
    freight_order_id = Column(Integer, ForeignKey("freight_orders.id"), nullable=True)
    
    trip_description = Column(String, nullable=True)
    start_engine_hours = Column(Float, nullable=True)
    end_engine_hours = Column(Float, nullable=True)

    destination_address = Column(String, nullable=True) # Campo completo para referência
    destination_street = Column(String(255), nullable=True)
    destination_neighborhood = Column(String(100), nullable=True)
    destination_city = Column(String(100), nullable=True)
    destination_state = Column(String(2), nullable=True)
    destination_cep = Column(String(9), nullable=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    freight_order = relationship("FreightOrder", back_populates="journeys")
    implement = relationship("Implement", back_populates="journeys")
    vehicle = relationship("Vehicle", back_populates="journeys")
    driver = relationship("User", back_populates="journeys")
    organization = relationship("Organization")
