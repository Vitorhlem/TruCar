import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class JourneyType(str, enum.Enum):
    SPECIFIC_DESTINATION = "specific_destination"
    FREE_ROAM = "free_roam"

class Journey(Base):
    __tablename__ = "journeys"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=DateTime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_mileage = Column(Integer, nullable=False)
    end_mileage = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    trip_type = Column(Enum(JourneyType), nullable=False)
    destination_address = Column(String, nullable=True)
    trip_description = Column(String, nullable=True)

    # --- NOVAS COLUNAS PARA AGRONEGÓCIO ---
    start_engine_hours = Column(Float, nullable=True)
    end_engine_hours = Column(Float, nullable=True)
    # --- FIM DAS NOVAS COLUNAS ---

    # Relacionamentos
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    vehicle = relationship("Vehicle", back_populates="journeys")
    driver = relationship("User", back_populates="journeys")
    organization = relationship("Organization") # Relação simples