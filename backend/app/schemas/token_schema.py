# backend/app/schemas/token_schema.py

from pydantic import BaseModel
from app.schemas.user_schema import UserPublic

# Este schema representa a parte do token da resposta
class Token(BaseModel):
    access_token: str
    token_type: str

# Este é o schema completo que o login.py está a tentar importar.
# Ele combina o Token e os dados públicos do utilizador.
class TokenData(BaseModel):
    user: UserPublic
    token: Token