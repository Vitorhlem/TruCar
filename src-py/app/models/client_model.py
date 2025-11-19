# ARQUIVO: backend/app/models/client_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relacionamento de volta para a Organização
    organization = relationship("Organization", back_populates="clients")
    
    # Relacionamento com as Ordens de Frete
    freight_orders = relationship("FreightOrder", back_populates="client", cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('name', 'organization_id', name='_client_name_org_uc'),
    )