from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class DemoUsage(Base):
    __tablename__ = 'demousage'
    
    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False, index=True)
    
    resource_type = Column(String, nullable=False, index=True)
    usage_count = Column(Integer, default=0)
    period = Column(Date, nullable=False)
    
    organization = relationship("Organization")