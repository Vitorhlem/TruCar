# backend/app/models/implement_model.py
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class ImplementStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"

class Implement(Base):
    __tablename__ = "implements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    # --- A COLUNA QUE CAUSOU O ERRO ---
    type = Column(String(50), nullable=True) # Ex: "Arado", "Plantadeira"
    # --- FIM ---
    status = Column(String(20), nullable=False, default=ImplementStatus.AVAILABLE)
    year = Column(Integer, nullable=False)
    identifier = Column(String(50), nullable=True) 

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="implements")

    # Esta relação pode precisar ser ajustada se o back_populates estiver errado
    # Verifique seu journey_model.py
    journeys = relationship("Journey", back_populates="implement")
