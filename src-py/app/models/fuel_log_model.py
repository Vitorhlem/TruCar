import enum
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class VerificationStatus(str, enum.Enum):
    VERIFIED = "Verificado"
    SUSPICIOUS = "Suspeito"
    UNVERIFIED = "Não verificado"
    PENDING = "Pendente" # Status para logs de integração antes da verificação

class FuelLogSource(str, enum.Enum):
    MANUAL = "MANUAL"
    INTEGRATION = "INTEGRATION"


class FuelLog(Base):
    """
    Modelo da tabela de Registros de Abastecimento, agora com campos para integração.
    """
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    odometer = Column(Integer, nullable=False)
    liters = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    receipt_photo_url = Column(String(512), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    verification_status = Column(SAEnum(VerificationStatus), nullable=False, default=VerificationStatus.UNVERIFIED)
    provider_transaction_id = Column(String(255), unique=True, nullable=True, index=True)
    provider_name = Column(String(100), nullable=True)
    gas_station_name = Column(String(255), nullable=True)
    gas_station_latitude = Column(Float, nullable=True)
    gas_station_longitude = Column(Float, nullable=True)

    source = Column(SAEnum(FuelLogSource), nullable=False, default=FuelLogSource.MANUAL)
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    organization = relationship("Organization", back_populates="fuel_logs")
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    user = relationship("User", back_populates="fuel_logs")
