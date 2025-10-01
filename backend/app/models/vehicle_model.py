import enum
from sqlalchemy import Column, Integer, String, Date, Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "Disponível"
    IN_USE = "Em uso"
    MAINTENANCE = "Em manutenção"

class Vehicle(Base):
    __tablename__ = "vehicles"
    

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=True)
    identifier = Column(String(50), nullable=True)
    year = Column(Integer, nullable=False)
    photo_url = Column(String(512), nullable=True)
    status = Column(SAEnum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)
    current_km = Column(Integer, nullable=False, default=0)
    current_engine_hours = Column(Float, nullable=True, default=0)
    axle_configuration = Column(String(10), nullable=True) 

    telemetry_device_id = Column(String(100), unique=True, index=True, nullable=True)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)
    
    next_maintenance_date = Column(Date, nullable=True)
    next_maintenance_km = Column(Integer, nullable=True)
    maintenance_notes = Column(Text, nullable=True)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="vehicles")

    journeys = relationship("Journey", back_populates="vehicle", cascade="all, delete-orphan")
    fuel_logs = relationship("FuelLog", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="vehicle", cascade="all, delete-orphan")
    freight_orders = relationship("FreightOrder", back_populates="vehicle")
    costs = relationship("VehicleCost", back_populates="vehicle", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="vehicle")

    # --- Relação com Documentos adicionada ---
    documents = relationship("Document", back_populates="vehicle", cascade="all, delete-orphan")
    components = relationship("VehicleComponent", back_populates="vehicle", cascade="all, delete-orphan")
    inventory_transactions = relationship("InventoryTransaction", back_populates="related_vehicle")
    tires = relationship("VehicleTire", back_populates="vehicle", cascade="all, delete-orphan")
