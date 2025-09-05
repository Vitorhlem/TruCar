import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    ForeignKey,
    Text,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class DocumentType(str, enum.Enum):
    CNH = "CNH"
    CRLV = "CRLV"
    ANTT = "ANTT"
    ASO = "ASO"
    SEGURO = "Seguro"
    OUTRO = "Outro"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(SAEnum(DocumentType), nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    file_url = Column(String(512), nullable=False)
    notes = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    organization = relationship("Organization", back_populates="documents")
    vehicle = relationship("Vehicle", back_populates="documents")
    driver = relationship("User", back_populates="documents")
