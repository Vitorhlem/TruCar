# backend/app/models/implement_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
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
    type = Column(String, nullable=True) # Ex: "Arado", "Plantadeira"
    status = Column(Enum(ImplementStatus), default=ImplementStatus.AVAILABLE)

    year = Column(Integer, nullable=False)
    identifier = Column(String(50), unique=True, nullable=True) # Ex: número de série ou patrimônio

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")

    journeys = relationship("Journey", back_populates="implement")