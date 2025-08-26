# backend/app/models/journey_model.py

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Float
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from .organization_model import Organization
from .user_model import User
from .vehicle_model import Vehicle
# IMPORTA o Enum a partir da nossa fonte da verdade (o schema).
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
    
    # --- AS DUAS LINHAS QUE ESTAVAM EM FALTA ---
    destination_address = Column(String, nullable=True)
    trip_description = Column(String, nullable=True)
    # --- FIM DAS LINHAS EM FALTA ---

    start_engine_hours = Column(Float, nullable=True)
    end_engine_hours = Column(Float, nullable=True)

    # Relacionamentos
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    vehicle = relationship("Vehicle", back_populates="journeys")
    driver = relationship("User", back_populates="journeys")
    organization = relationship("Organization")