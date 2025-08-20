from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import date
from fastapi.responses import Response
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io


from app import crud
from app.api import deps
from app.models.user_model import User, UserRole
from app.models.vehicle_model import VehicleStatus
from app.schemas.journey_schema import JourneyCreate, JourneyUpdate, JourneyPublic, EndJourneyResponse

router = APIRouter()

@router.get("/{journey_id}/pdf", response_class=Response)
async def get_journey_report_pdf(
    journey_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Gera um relatório em PDF para uma viagem específica.
    """
    journey = await crud.journey.get_journey(db, journey_id=journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")

    # Configura o Jinja2 para ler o template
    env = Environment(loader=FileSystemLoader("app/templates/"))
    template = env.get_template("journey_report.html")
    html_content = template.render(journey=journey)

    # Converte o HTML renderizado para PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        return Response(
            result.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_viagem_{journey_id}.pdf"}
        )
    else:
        raise HTTPException(status_code=500, detail="Erro ao gerar o PDF.")

@router.get("/", response_model=List[JourneyPublic])
async def read_journeys(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0, limit: int = 100, driver_id: int | None = None,
    vehicle_id: int | None = None, date_from: date | None = None,
    date_to: date | None = None, current_user: User = Depends(deps.get_current_active_user)
):
    if date_to and date_from and date_to < date_from:
        raise HTTPException(status_code=400, detail="A data final não pode ser anterior à data inicial.")
    final_driver_id_filter = driver_id
    if current_user.role == UserRole.DRIVER:
        final_driver_id_filter = current_user.id
    journeys = await crud.journey.get_all_journeys(
        db, organization_id=current_user.organization_id, # Adicionado
        # ... (outros filtros)
    )
    return journeys

@router.post("/start", response_model=JourneyPublic, status_code=status.HTTP_201_CREATED)
async def start_journey(*, db: AsyncSession = Depends(deps.get_db), journey_in: JourneyCreate, current_user: User = Depends(deps.get_current_active_user)):
    active_journey = await crud.journey.get_active_journey_by_driver(db, driver_id=current_user.id)
    if active_journey:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O motorista já possui uma viagem em andamento.")
    vehicle = await crud.vehicle.get_vehicle(db, vehicle_id=journey_in.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado.")
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"O veículo (placa: {vehicle.license_plate}) não está disponível.")
    new_journey = await crud.journey.create_journey(db=db, journey_in=journey_in, driver_id=current_user.id)
    return new_journey

@router.put("/{journey_id}/end", response_model=EndJourneyResponse) # <-- Altere o response_model
async def end_journey(
    *,
    db: AsyncSession = Depends(deps.get_db),
    journey_id: int,
    journey_in: JourneyUpdate,
    current_user: User = Depends(deps.get_current_active_user)
):
    journey_to_end = await crud.journey.get_journey(db, journey_id=journey_id)
    if not journey_to_end:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    if not journey_to_end.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Esta viagem já foi finalizada.")
    if journey_to_end.driver_id != current_user.id and current_user.role != UserRole.MANAGER:
        raise HTTPException(status_code=403, detail="Apenas o motorista da viagem ou um gestor podem finalizá-la.")
    if journey_in.end_mileage < journey_to_end.start_mileage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A quilometragem final não pode ser menor que a inicial.")
    finished_journey, updated_vehicle = await crud.journey.end_journey(
        db=db, journey_to_update=journey_to_end, journey_in=journey_in
    )
    return {"journey": finished_journey, "vehicle": updated_vehicle}    

@router.get("/active", response_model=List[JourneyPublic])
async def get_active_journeys(db: AsyncSession = Depends(deps.get_db), current_user: User = Depends(deps.get_current_active_user)):
    active_journeys = await crud.journey.get_active_journeys(db)
    return active_journeys

@router.delete("/{journey_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journey(*, db: AsyncSession = Depends(deps.get_db), journey_id: int, current_user: User = Depends(deps.get_current_active_manager)) -> Response:
    deleted_journey = await crud.journey.delete_journey(db=db, journey_id=journey_id)
    if not deleted_journey:
        raise HTTPException(status_code=404, detail="Viagem não encontrada.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)