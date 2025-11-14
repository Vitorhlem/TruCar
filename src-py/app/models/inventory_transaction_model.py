import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class TransactionType(str, enum.Enum):
    ENTRADA = "Entrada"
    # --- CORREÇÃO DE TEXTO RECOMENDADA ---
    # Altere o texto aqui para refletir melhor a ação
    SAIDA_USO = "Instalação (Uso)" 
    # --- FIM DA CORREÇÃO ---
    FIM_DE_VIDA = "Fim de Vida"
    # RETORNO_ESTOQUE = "Retorno"  <-- REMOVIDO
    AJUSTE_INICIAL = "Ajuste Inicial" # Mantido para a criação de itens
    # AJUSTE_MANUAL = "Ajuste Manual" <-- REMOVIDO
    INSTALACAO = "Instalação"
    DESCARTE = "Descarte"

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # --- COLUNAS DE QUANTIDADE REMOVIDAS ---
    # quantity_change = Column(Integer, nullable=False)
    # stock_after_transaction = Column(Integer, nullable=False)

    # --- RELAÇÃO PRINCIPAL ATUALIZADA ---
    # Aponta para o item específico, não para o "template"
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=True) # Mantém para referência do template
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    
    notes = Column(Text, nullable=True)
    related_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # --- RELACIONAMENTOS ATUALIZADOS ---
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