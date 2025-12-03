import enum
from typing import TYPE_CHECKING, List, Optional
from datetime import date
# Adicione UniqueConstraint aos imports
from sqlalchemy import Column, Integer, String, Date, Text, Float, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base

if TYPE_CHECKING:
    from .organization_model import Organization
    from .journey_model import Journey
    from .fuel_log_model import FuelLog
    from .maintenance_model import MaintenanceRequest
    from .freight_order_model import FreightOrder
    from .vehicle_cost_model import VehicleCost
    from .alert_model import Alert
    from .document_model import Document
    from .vehicle_component_model import VehicleComponent
    from .inventory_transaction_model import InventoryTransaction
    from .tire_model import VehicleTire
    from .fine_model import Fine
    from .location_history_model import LocationHistory

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "Disponível"
    IN_USE = "Em uso"
    MAINTENANCE = "Em manutenção"

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # --- CORREÇÃO: Removido unique=True global ---
    license_plate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    identifier: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # ---------------------------------------------
    
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[VehicleStatus] = mapped_column(SAEnum(VehicleStatus), nullable=False, default=VehicleStatus.AVAILABLE)
    current_km: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_engine_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0)
    axle_configuration: Mapped[Optional[str]] = mapped_column(String(30), nullable=True) 

    # --- CORREÇÃO: Removido unique=True global ---
    telemetry_device_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    # ---------------------------------------------
    
    last_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    next_maintenance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_maintenance_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    maintenance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)
    location_history: Mapped[List["LocationHistory"]] = relationship("LocationHistory", back_populates="vehicle", cascade="all, delete-orphan")
    
    # Relações (Mantidas)
    organization: Mapped["Organization"] = relationship("Organization", back_populates="vehicles")
    journeys: Mapped[List["Journey"]] = relationship("Journey", back_populates="vehicle", cascade="all, delete-orphan")
    fuel_logs: Mapped[List["FuelLog"]] = relationship("FuelLog", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_requests: Mapped[List["MaintenanceRequest"]] = relationship("MaintenanceRequest", back_populates="vehicle", cascade="all, delete-orphan")
    freight_orders: Mapped[List["FreightOrder"]] = relationship("FreightOrder", back_populates="vehicle")
    costs: Mapped[List["VehicleCost"]] = relationship("VehicleCost", back_populates="vehicle", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="vehicle")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="vehicle", cascade="all, delete-orphan")
    components: Mapped[List["VehicleComponent"]] = relationship("VehicleComponent", back_populates="vehicle", cascade="all, delete-orphan")
    inventory_transactions: Mapped[List["InventoryTransaction"]] = relationship("InventoryTransaction", back_populates="related_vehicle")
    tires: Mapped[List["VehicleTire"]] = relationship("VehicleTire", back_populates="vehicle", cascade="all, delete-orphan")
    fines: Mapped[List["Fine"]] = relationship("Fine", back_populates="vehicle", cascade="all, delete-orphan")

    # --- CORREÇÃO FINAL: Unicidade Composta ---
    __table_args__ = (
        # A placa só precisa ser única DENTRO da mesma organização
        UniqueConstraint('license_plate', 'organization_id', name='_vehicle_license_org_uc'),
        # O identificador (ex: Frota 01) também
        UniqueConstraint('identifier', 'organization_id', name='_vehicle_identifier_org_uc'),
        # Dispositivos de telemetria geralmente são únicos globalmente (físicos), 
        # mas se você quiser permitir reuso em orgs diferentes, use assim:
        UniqueConstraint('telemetry_device_id', 'organization_id', name='_vehicle_telemetry_org_uc'),
    )