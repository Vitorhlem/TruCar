from pydantic import BaseModel
from datetime import datetime
from typing import Optional # Importar Optional
from .part_schema import PartPublic

# 1. IMPORTAR O NOVO SCHEMA SIMPLES
from .inventory_transaction_schema import TransactionForComponent 

class VehicleComponentBase(BaseModel):
    part_id: int
    quantity: int 

class VehicleComponentCreate(VehicleComponentBase):
    pass

class VehicleComponentPublic(BaseModel):
    id: int
    installation_date: datetime
    uninstallation_date: datetime | None
    is_active: bool
    part: PartPublic

    # 2. SUBSTITUIR O TIPO DA TRANSAÇÃO
    # Trocamos 'TransactionPublic' por 'TransactionForComponent'.
    # Isso quebra a cadeia de validação que causava o erro 500
    # e ainda resolve o problema do "N/A" (pois o 'user' está incluído).
    inventory_transaction: Optional[TransactionForComponent] = None

    class Config:
        from_attributes = True