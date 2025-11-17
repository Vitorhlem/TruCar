import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class TransactionType(str, enum.Enum):
    ENTRADA = "Entrada"
    SAIDA_USO = "Instalação (Uso)" 
    FIM_DE_VIDA = "Fim de Vida"
    AJUSTE_INICIAL = "Ajuste Inicial" # Mantido para a criação de itens
    INSTALACAO = "Instalação"
    DESCARTE = "Descarte"

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    

    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True) # Mantém para referência do template
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    
    notes = Column(Text, nullable=True)
    related_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    item = relationship("InventoryItem", back_populates="transactions")
    part_template = relationship("Part", back_populates="transactions") # Relação opcional
    
    user = relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="inventory_transactions_performed"
    )
    
    related_vehicle = relationship(
        "Vehicle", 
        back_populates="inventory_transactions"
    )
    
    related_user = relationship(
        "User", 
        foreign_keys=[related_user_id], 
        back_populates="inventory_transactions_received"
    )

    vehicle_component = relationship(
        "VehicleComponent", 
        back_populates="inventory_transaction", 
        uselist=False
    )