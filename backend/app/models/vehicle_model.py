# backend/app/models/vehicle_model.py
from sqlalchemy import Column, Integer, String, Enum, Date, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "Disponível"
    IN_USE = "Em uso"
    MAINTENANCE = "Em manutenção"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False, index=True)
    license_plate = Column(String(20), unique=True, index=True, nullable=True)
    identifier = Column(String(50), index=True, nullable=True)
    year = Column(Integer, nullable=False)
    photo_url = Column(String(512), nullable=True)
    status = Column(Enum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)
    current_km = Column(Integer, nullable=False, default=0)
    current_engine_hours = Column(Float, nullable=True, default=0)
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_km = Column(Integer, nullable=True)
    maintenance_notes = Column(Text, nullable=True)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    organization = relationship("Organization", back_populates="vehicles")
    journeys = relationship("Journey", back_populates="vehicle")