import enum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False, index=True)
    license_plate = Column(String(10), unique=True, index=True, nullable=False)
    year = Column(Integer, nullable=False)
    photo_url = Column(String(255), nullable=True)
    status = Column(Enum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)

    # Versão sem a regra de cascade
    journeys = relationship("Journey", back_populates="vehicle")