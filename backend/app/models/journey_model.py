import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    DateTime,
    Boolean,
    Text
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class JourneyType(str, enum.Enum):
    """
    Define o tipo de viagem, conforme sua ideia original.
    Isso nos dá flexibilidade para lidar com diferentes cenários de uso.
    """
    SPECIFIC_DESTINATION = "specific_destination"
    FREE_ROAM = "free_roam" # O modo "Livre" para ir ao centro, etc.


class Journey(Base):
    """
    Modelo da tabela de Viagens (Journeys).
    
    Esta é a tabela principal de "eventos" do sistema. Cada registro aqui
    representa uma única viagem realizada com um veículo da frota.
    """
    __tablename__ = "journeys"

    id = Column(Integer, primary_key=True, index=True)

    # Chaves Estrangeiras - Os links para os outros modelos
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    # Dados da viagem
    start_mileage = Column(Integer, nullable=False)
    end_mileage = Column(Integer, nullable=True) # Nulo até a viagem terminar

    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True) # Nulo até a viagem terminar
    
    trip_type = Column(Enum(JourneyType), nullable=False, default=JourneyType.SPECIFIC_DESTINATION)
    destination_address = Column(String(255), nullable=True)
    trip_description = Column(Text, nullable=True) # Campo para descrever a viagem "Livre"

    is_active = Column(Boolean, default=True, nullable=False) # Flag para viagens em andamento

    # Relacionamentos Reversos - Completam os links definidos nos outros modelos
    driver = relationship("User", back_populates="journeys")
    vehicle = relationship("Vehicle", back_populates="journeys")