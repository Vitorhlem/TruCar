import enum
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# Enum para padronizar os tipos de custo
class CostType(str, enum.Enum):
    MANUTENCAO = "Manutenção"
    COMBUSTIVEL = "Combustível"
    PEDAGIO = "Pedágio" # Pedágio = Toll
    SEGURO = "Seguro" # Seguro = Insurance
    PNEU = "Pneu" # Pneu = Tire
    OUTROS = "Outros"

class VehicleCost(Base):
    __tablename__ = "vehicle_costs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    cost_type = Column(SAEnum(CostType), nullable=False)
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    vehicle = relationship("Vehicle", back_populates="costs")
    
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
