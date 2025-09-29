from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base_class import Base

# NOVO: Enum para categorizar os itens do inventário
class PartCategory(str, enum.Enum):
    PECA = "Peça"
    FLUIDO = "Fluído"
    CONSUMIVEL = "Consumível"
    OUTRO = "Outro"

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    
    # NOVO: Campo de categoria adicionado
    category = Column(SAEnum(PartCategory), nullable=False, default=PartCategory.PECA)

    part_number = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, nullable=False, default=0)
    location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(512), nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")

    # NOVO: Relação com o histórico de transações
    transactions = relationship("InventoryTransaction", back_populates="part", cascade="all, delete-orphan")