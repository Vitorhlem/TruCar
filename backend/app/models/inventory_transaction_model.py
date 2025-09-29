import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# Define os tipos de movimentação de estoque
class TransactionType(str, enum.Enum):
    ENTRADA = "Entrada"          # Adicionar itens ao estoque (compra, etc.)
    SAIDA_USO = "Saída para Uso"   # "Dar" - Atribuir a um veículo/serviço
    SAIDA_FIM_DE_VIDA = "Fim de Vida" # Descartar um item
    RETORNO_ESTOQUE = "Retorno"  # Estornar um item que não foi usado
    AJUSTE_INICIAL = "Ajuste Inicial" # Carga inicial do sistema
    AJUSTE_MANUAL = "Ajuste Manual"   # Correção de contagem

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    quantity_change = Column(Integer, nullable=False) # Positivo para entradas, negativo para saídas
    stock_after_transaction = Column(Integer, nullable=False)
    
    notes = Column(Text, nullable=True)
    # Campos para rastrear a quem/onde o item foi "dado"
    related_vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relacionamentos
    part = relationship("Part", back_populates="transactions")
    user = relationship("User", foreign_keys=[user_id])
    related_vehicle = relationship("Vehicle")
    related_user = relationship("User", foreign_keys=[related_user_id])