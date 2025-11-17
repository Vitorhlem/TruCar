from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class VehicleComponent(Base):
    """
    Modelo que representa um componente (peça) instalado em um veículo.
    """
    __tablename__ = "vehicle_components"

    id = Column(Integer, primary_key=True, index=True)
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    inventory_transaction_id = Column(Integer, ForeignKey("inventory_transactions.id"), unique=True, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    installation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uninstallation_date = Column(DateTime(timezone=True), nullable=True) # Data de descarte
    
    vehicle = relationship("Vehicle", back_populates="components")
    part = relationship("Part")
    transaction = relationship("InventoryTransaction")
    inventory_transaction = relationship("InventoryTransaction", back_populates="vehicle_component")
