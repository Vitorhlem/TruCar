from pydantic import BaseModel
from typing import Optional

from .user_schema import UserPublic

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic