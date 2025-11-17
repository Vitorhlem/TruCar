from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.schemas.telemetry_schema import TelemetryPayload
from app import deps
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud # <-- CAMINHO CORRETO


router = APIRouter()

@router.post("/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_telemetry(
    *,
    db: AsyncSession = Depends(deps.get_db),
    payload: TelemetryPayload
):
    """Recebe e processa um pacote de dados de telemetria."""
    await crud.vehicle.update_vehicle_from_telemetry(db=db, payload=payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)