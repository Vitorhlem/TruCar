from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, deps
from app.schemas.gps_schema import LocationCreate

router = APIRouter()

@router.post("/ping", status_code=204)
async def receive_gps_ping(
    *,
    db: AsyncSession = Depends(deps.get_db),
    location_in: LocationCreate,
    # Em produção, a autenticação seria feita por um token de dispositivo, não de usuário
    # current_user: models.user_model.User = Depends(deps.get_current_active_user)
):
    """
    Recebe um 'ping' de localização e atualiza o estado do veículo.
    Este será nosso endpoint de teste e, futuramente, o usado pelo OBD-II.
    """
    await crud.vehicle.update_location(
        db=db,
        vehicle_id=location_in.vehicle_id,
        lat=location_in.latitude,
        lon=location_in.longitude
    )
    # Não retornamos conteúdo para máxima performance
    return