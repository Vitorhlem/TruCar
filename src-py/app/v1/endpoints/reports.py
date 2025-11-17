from fastapi import APIRouter, Depends, HTTPException, Response, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
from datetime import datetime, date, timedelta
import logging
from app import crud, deps
from app.models.user_model import User, UserRole
from app.schemas.report_generator_schema import ReportRequest
from app.schemas.report_schema import (
    DashboardSummary, 
    VehicleConsolidatedReport, 
    DriverPerformanceReport, 
    FleetManagementReport,
    VehicleReportRequest  # <-- Importa o novo schema de request
)

router = APIRouter()

@router.post("/fleet-management", response_model=FleetManagementReport,
             dependencies=[Depends(deps.check_demo_limit("reports"))])
async def generate_fleet_management_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    start_date: date = Body(..., embed=True),
    end_date: date = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Gera um relatório gerencial com KPIs e rankings de toda a frota."""
    try:
        report_data = await crud.report.get_fleet_management_data(
            db=db, start_date=start_date, end_date=end_date, organization_id=current_user.organization_id
        )
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="reports")
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao gerar o relatório gerencial.")

@router.post("/driver-performance", response_model=DriverPerformanceReport,
             dependencies=[Depends(deps.check_demo_limit("reports"))])
async def generate_driver_performance_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    start_date: date = Body(..., embed=True),
    end_date: date = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Gera um relatório de desempenho com ranking de todos os motoristas."""
    try:
        report_data = await crud.report.get_driver_performance_data(
            db=db, start_date=start_date, end_date=end_date, organization_id=current_user.organization_id
        )
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="reports")
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao gerar o relatório: {e}")

@router.post("/generate-pdf", response_class=Response,
             dependencies=[Depends(deps.check_demo_limit("reports"))])
async def generate_report_pdf(
    *,
    db: AsyncSession = Depends(deps.get_db),
    report_request: ReportRequest,
    current_user: User = Depends(deps.get_current_active_user),
):
    """Endpoint central para gerar relatórios em PDF de forma segura."""
    env = Environment(loader=FileSystemLoader("app/templates/"))
    try:
        if report_request.report_type == "activity_by_driver":
            template = env.get_template("driver_activity_report.html")
            data = await crud.report.get_driver_activity_data(
                db, driver_id=report_request.target_id, organization_id=current_user.organization_id,
                date_from=report_request.date_from, date_to=report_request.date_to
            )
            filename = f"relatorio_motorista_{report_request.target_id}.pdf"
        else:
            raise HTTPException(status_code=400, detail="Tipo de relatório inválido.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not data:
        raise HTTPException(status_code=404, detail="Não foram encontrados dados para este relatório.")

    html_content = template.render(data=data)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="reports")
        return Response(
            result.getvalue(), media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        raise HTTPException(status_code=500, detail="Erro ao gerar o PDF.")
    

@router.post("/vehicle-consolidated", response_model=VehicleConsolidatedReport,
             dependencies=[Depends(deps.check_demo_limit("reports"))])
async def generate_vehicle_consolidated_report(
    *,
    db: AsyncSession = Depends(deps.get_db),
    report_request: VehicleReportRequest = Body(...), 
    current_user: User = Depends(deps.get_current_active_user),
):
    """Gera um relatório consolidado com todos os dados de um veículo."""
    try:
        report_data = await crud.report.get_vehicle_consolidated_data(
            db=db,
            vehicle_id=report_request.vehicle_id,
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            sections=report_request.sections, # <-- Passa as seções selecionadas
            organization_id=current_user.organization_id
        )
        if current_user.role == UserRole.CLIENTE_DEMO:
            await crud.demo_usage.increment_usage(db, organization_id=current_user.organization_id, resource_type="reports")
        return report_data
    except ValueError as e:
        logging.error(f"Erro de Valor no CRUD do Relatório: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro Interno ao processar dados do relatório: {e}")
    except Exception as e:
        logging.error(f"Erro Inesperado no Relatório: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao gerar o relatório: {e}")

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary_data(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    summary_data = await crud.report.get_dashboard_summary(
        db, current_user=current_user, start_date=thirty_days_ago
    )
    return summary_data