from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Quem realizou a ação?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # O que aconteceu?
    action = Column(String(50), nullable=False, index=True) # Ex: CREATE, UPDATE, DELETE, LOGIN
    resource_type = Column(String(50), nullable=False, index=True) # Ex: user, vehicle, cost
    resource_id = Column(String(50), nullable=True) # ID do objeto afetado (pode ser string ou int)
    
    # Detalhes (JSON para flexibilidade)
    # Ex: {"old_value": "Azul", "new_value": "Vermelho"}
    details = Column(JSON, nullable=True)
    
    # Metadados
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relacionamentos
    user = relationship("User")
    organization = relationship("Organization")