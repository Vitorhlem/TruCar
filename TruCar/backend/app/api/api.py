from fastapi import APIRouter

from app.api.v1.endpoints import users, vehicles, journeys, login # <-- Importe login

# Roteador principal da API
api_router = APIRouter()

# Inclui o roteador de usuários, definindo um prefixo e uma tag.
# O prefixo garante que todas as rotas em users.py começarão com /users.
# A tag agrupa essas rotas na documentação automática da API.
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(journeys.router, prefix="/journeys", tags=["Journeys"])
api_router.include_router(login.router, prefix="/login", tags=["Login"]) 