import enum
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# --- NOVO ENUM ADICIONADO ---
# Define os possíveis status de uma transação de combustível
class VerificationStatus(str, enum.Enum):
    VERIFIED = "Verificado"      # Localização do veículo e do posto coincidem
    SUSPICIOUS = "Suspeito"      # Discrepância entre as localizações
    UNVERIFIED = "Não verificado"  # Importado, mas ainda não processado
    MANUAL = "Manual"          # Lançamento feito manualmente pelo usuário

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
    
    # --- NOVOS CAMPOS PARA INTEGRAÇÃO ---
    # Estes campos serão preenchidos automaticamente pela integração
    verification_status = Column(SAEnum(VerificationStatus), nullable=False, default=VerificationStatus.MANUAL)
    provider_transaction_id = Column(String(255), unique=True, nullable=True, index=True) # ID único da transação no provedor (ex: Ticket Log)
    provider_name = Column(String(100), nullable=True) # Nome do provedor
    gas_station_name = Column(String(255), nullable=True)
    gas_station_latitude = Column(Float, nullable=True)
    gas_station_longitude = Column(Float, nullable=True)
    # --- FIM DA ADIÇÃO ---

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relacionamentos atualizados para seguir o padrão `back_populates`
    organization = relationship("Organization", back_populates="fuel_logs")
    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    user = relationship("User", back_populates="fuel_logs")
