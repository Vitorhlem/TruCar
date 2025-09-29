from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Part(Base):
    __tablename__ = "parts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    part_number = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)
    
    # --- CORREÇÃO: Renomeado de 'quantity' para 'stock' ---
    stock = Column(Integer, nullable=False, default=0)
    # --- FIM DA CORREÇÃO ---

    min_stock = Column(Integer, nullable=False, default=0)
    location = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    photo_url = Column(String(512), nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")