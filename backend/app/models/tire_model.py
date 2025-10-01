from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class VehicleTire(Base):
    """
    Modelo que representa um pneu específico instalado em um veículo.
    Cada registro é um ciclo de vida de um pneu em uma posição.
    """
    __tablename__ = "vehicle_tires"

    id = Column(Integer, primary_key=True, index=True)
    
    # Chaves estrangeiras
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False) # O Pneu (do inventário)

    # Dados da Instalação
    position_code = Column(String(50), nullable=False) # Ex: "1L" (Eixo 1, Esquerdo), "2RI" (Eixo 2, Direito Interno)
    install_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    install_km = Column(Integer, nullable=False) # KM do veículo no momento da instalação

    # Dados da Remoção/Descarte
    is_active = Column(Integer, default=1, nullable=False) # 1 para ativo, 0 para inativo (descartado/movido)
    removal_date = Column(DateTime(timezone=True), nullable=True)
    removal_km = Column(Integer, nullable=True)
    total_km_run = Column(Integer, nullable=True) # Calculado no momento da remoção

    # Relacionamentos
    vehicle = relationship("Vehicle", back_populates="tires")
    part = relationship("Part")