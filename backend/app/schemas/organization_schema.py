from pydantic import BaseModel
from typing import Optional

# --- CORRIGIDO ---
# Removemos a importação do PlanStatus, que já não existe
from app.models.organization_model import Sector
# --- FIM DA CORREÇÃO ---


class OrganizationBase(BaseModel):
    name: str
    sector: Sector


class OrganizationCreate(OrganizationBase):
    # O campo plan_status foi REMOVIDO daqui
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[Sector] = None
    # O campo plan_status foi REMOVIDO daqui


class OrganizationPublic(OrganizationBase):
    id: int
    # O campo plan_status foi REMOVIDO daqui

    model_config = { "from_attributes": True }