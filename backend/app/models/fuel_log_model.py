from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class FuelLog(Base):
    """
    Modelo da tabela de Registros de Abastecimento.
    """
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    odometer = Column(Integer, nullable=False) # KM do odômetro no momento
    liters = Column(Float, nullable=False) # Litros abastecidos
    total_cost = Column(Float, nullable=False) # Custo total em R$
    
    # Links para o veículo e o usuário que registrou
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    receipt_photo_url = Column(String(512), nullable=True) # URL da foto do comprovante
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")
    vehicle = relationship("Vehicle")
    user = relationship("User")