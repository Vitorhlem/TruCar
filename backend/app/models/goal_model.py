from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    target_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False) # Ex: 'R$', 'km/l', '%'
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    organization = relationship("Organization", back_populates="goals")
