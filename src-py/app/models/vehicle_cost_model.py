import enum
from typing import TYPE_CHECKING, Optional
from datetime import date
from sqlalchemy import Column, Integer, String, Date as SADate, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base

if TYPE_CHECKING:
    from .vehicle_model import Vehicle
    from .fine_model import Fine  # <-- Importar a Multa

# Enum para padronizar os tipos de custo
class CostType(str, enum.Enum):
    MANUTENCAO = "Manutenção"
    COMBUSTIVEL = "Combustível"
    PEDAGIO = "Pedágio"
    SEGURO = "Seguro"
    PNEU = "Pneu"
    PECAS_COMPONENTES = "Peças e Componentes"
    MULTA = "Multa"
    OUTROS = "Outros"

class VehicleCost(Base):
    __tablename__ = "vehicle_costs"

    # --- REESCRITO COM SINTAXE MODERNA (Mapped) ---
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[date] = mapped_column(SADate, nullable=False)
    cost_type: Mapped[CostType] = mapped_column(SAEnum(CostType), nullable=False)
    
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicles.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(Integer, ForeignKey("organizations.id"), nullable=False)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="costs")
    
    # --- ADIÇÃO DA LIGAÇÃO DIRETA ---
    # Isso cria a coluna vehicle_costs.fine_id
    # O unique=True garante que um custo só pode estar ligado a UMA multa (1-para-1)
    fine_id: Mapped[Optional[int]] = mapped_column(ForeignKey("fines.id", ondelete="SET NULL"), nullable=True, unique=True)
    
    # Isso permite acessar a multa a partir do custo (cost.fine)
    fine: Mapped[Optional["Fine"]] = relationship("Fine", back_populates="cost")