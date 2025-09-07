import enum
from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Sector(str, enum.Enum):
    AGRONEGOCIO = "agronegocio"
    CONSTRUCAO_CIVIL = "construcao_civil"
    SERVICOS = "servicos"
    FRETE = "frete"

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    sector = Column(String(50), nullable=False)
    
    # --- CAMPOS PARA INTEGRAÇÃO DE COMBUSTÍVEL ADICIONADOS ---
    fuel_provider_name = Column(String(100), nullable=True)
    encrypted_fuel_provider_api_key = Column(LargeBinary, nullable=True)
    encrypted_fuel_provider_api_secret = Column(LargeBinary, nullable=True)
    # --- FIM DA ADIÇÃO ---

    users = relationship("User", back_populates="organization")
    vehicles = relationship("Vehicle", back_populates="organization")
    implements = relationship("Implement", back_populates="organization")
    clients = relationship("Client", back_populates="organization")
    freight_orders = relationship("FreightOrder", back_populates="organization")
    alerts = relationship("Alert", back_populates="organization")
    goals = relationship("Goal", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    fuel_logs = relationship("FuelLog", back_populates="organization")

