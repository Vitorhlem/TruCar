from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, Dict

class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    user_id: int
    organization_id: int
    ip_address: Optional[str] = None

class AuditLogPublic(AuditLogBase):
    id: int
    user_id: Optional[int]
    user_name: Optional[str] = None # Para exibir o nome na tabela
    created_at: datetime
    
    class Config:
        from_attributes = True