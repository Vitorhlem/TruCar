import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, Float, Text
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
    type = Column(String(50), nullable=True) # Ex: "Arado", "Plantadeira"
    status = Column(String(20), nullable=False, default=ImplementStatus.AVAILABLE)
    year = Column(Integer, nullable=False)
    identifier = Column(String(50), nullable=True) 

    acquisition_date = Column(Date, nullable=True)
    acquisition_value = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="implements")

    journeys = relationship("Journey", back_populates="implement")