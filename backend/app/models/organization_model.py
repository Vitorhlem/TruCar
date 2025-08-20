# backend/app/models/organization_model.py

import enum
from sqlalchemy import Column, Integer, String, Enum
# Garanta que o 'relationship' está a ser importado do sqlalchemy.orm
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Sector(str, enum.Enum):
    AGRONEGOCIO = "agronegocio"
    CONSTRUCAO_CIVIL = "construcao_civil"
    SERVICOS = "servicos"

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    sector = Column(Enum(Sector), nullable=False)

    # Relacionamentos de mão dupla
    users = relationship("User", back_populates="organization")
    
    # --- A LINHA QUE ESTAVA EM FALTA ---
    # Define a lista de veículos que pertencem a esta organização.
    vehicles = relationship("Vehicle", back_populates="organization")
    # --- FIM DA LINHA EM FALTA ---