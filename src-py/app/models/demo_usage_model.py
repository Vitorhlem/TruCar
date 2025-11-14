# backend/app/models/demo_usage_model.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DemoUsage(Base):
    __tablename__ = 'demousage'
    
    id = Column(Integer, primary_key=True, index=True)

    # --- ESTA É A CORREÇÃO DEFINITIVA ---
    # A referência da ForeignKey agora aponta para 'organizations.id' (plural),
    # que é o nome correto da tabela definido em organization_model.py.
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False, index=True)
    # --- FIM DA CORREÇÃO ---
    
    resource_type = Column(String, nullable=False, index=True)
    usage_count = Column(Integer, default=0)
    period = Column(Date, nullable=False)
    
    organization = relationship("Organization")