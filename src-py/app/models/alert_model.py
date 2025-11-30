import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Float, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class AlertLevel(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class AlertType(str, enum.Enum):
    GENERIC = "GENERIC"
    SPEEDING = "SPEEDING"
    ROAD_HAZARD = "ROAD_HAZARD"
    MAINTENANCE = "MAINTENANCE"
    FRAUD = "FRAUD"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255), nullable=False)
    level = Column(SAEnum(AlertLevel), nullable=False, default=AlertLevel.INFO)
    type = Column(SAEnum(AlertType), nullable=False, default=AlertType.GENERIC)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    organization = relationship("Organization", back_populates="alerts")
    vehicle = relationship("Vehicle", back_populates="alerts")
    driver = relationship("User", back_populates="alerts")