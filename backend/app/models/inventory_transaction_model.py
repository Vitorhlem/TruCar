import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class TransactionType(str, enum.Enum):
    ENTRADA = "Entrada"
    SAIDA_USO = "Saída para Uso"
    SAIDA_FIM_DE_VIDA = "Fim de Vida"
    RETORNO_ESTOQUE = "Retorno"
    AJUSTE_INICIAL = "Ajuste Inicial"
    AJUSTE_MANUAL = "Ajuste Manual"

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    stock_after_transaction = Column(Integer, nullable=False)
    
    notes = Column(Text, nullable=True)
    related_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- RELACIONAMENTOS CORRIGIDOS ---
    part = relationship("Part", back_populates="transactions")
    
    user = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="inventory_transactions_performed" # Liga ao User que realizou a ação
    )
    
    related_vehicle = relationship(
        "Vehicle", 
        back_populates="inventory_transactions" # Liga ao Veículo
    )
    
    related_user = relationship(
        "User", 
        foreign_keys=[related_user_id], 
        back_populates="inventory_transactions_received" # Liga ao User que recebeu o item
    )

    vehicle_component = relationship(
        "VehicleComponent", 
        back_populates="inventory_transaction", 
        uselist=False
    )