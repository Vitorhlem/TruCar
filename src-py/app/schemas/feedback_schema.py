from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedbackCreate(BaseModel):
    type: str # 'BUG', 'SUGESTAO', 'OUTRO'
    message: str

class FeedbackResponse(BaseModel):
    id: int
    type: str
    message: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True