from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# CORREÇÃO AQUI:
from app import deps 
from app.services.route_service import RouteService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    dest_lat: float
    dest_lon: float

@router.post("/calculate")
async def calculate_safe_route(
    data: RouteRequest,
    db: AsyncSession = Depends(deps.get_db),
    # Adicione autenticação se necessário:
    # current_user = Depends(deps.get_current_active_user)
):
    """
    Calcula rota segura evitando tempestades conhecidas.
    """
    route = await RouteService.get_optimized_route(
        data.start_lat, data.start_lon,
        data.dest_lat, data.dest_lon,
        db
    )
    
    if not route:
        raise HTTPException(status_code=400, detail="Não foi possível calcular a rota.")
        
    return route