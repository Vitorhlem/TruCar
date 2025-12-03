from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

from app.db.base_class import Base

class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=True) 
    
    timestamp = Column(DateTime, default=datetime.utcnow)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="location_history")
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization")