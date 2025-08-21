from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import io
from datetime import datetime, timedelta

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.report_generator_schema import ReportRequest
from app.schemas.report_schema import DashboardSummary

router = APIRouter()

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary_data(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """Retorna os dados agregados para o dashboard do gestor."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    summary_data = await crud.report.get_dashboard_summary(
        db, current_user=current_user, start_date=thirty_days_ago
    )
    return summary_data

@router.post("/generate-pdf", response_class=Response) # Mudei o nome da rota para ser mais específico
async def generate_report_pdf(
    *,
    db: AsyncSession = Depends(deps.get_db),
    report_request: ReportRequest,
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Endpoint central para gerar relatórios em PDF de forma segura.
    """
    env = Environment(loader=FileSystemLoader("app/templates/"))
    
    try:
        if report_request.report_type == "activity_by_driver":
            template = env.get_template("driver_activity_report.html")
            
            # A CORREÇÃO DE SEGURANÇA: Passamos a organization_id do gestor logado
            data = await crud.report.get_driver_activity_data(
                db,
                driver_id=report_request.target_id,
                organization_id=current_user.organization_id, # <-- A LINHA CRUCIAL
                date_from=report_request.date_from,
                date_to=report_request.date_to
            )
            filename = f"relatorio_motorista_{report_request.target_id}.pdf"
        
        else:
            raise HTTPException(status_code=400, detail="Tipo de relatório inválido.")

    except ValueError as e:
        # Captura o erro do CRUD se o motorista não for encontrado na organização
        raise HTTPException(status_code=404, detail=str(e))

    if not data:
         raise HTTPException(status_code=404, detail="Não foram encontrados dados para este relatório.")

    html_content = template.render(data=data)
    
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result)
    
    if not pdf.err:
        return Response(
            result.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:
        raise HTTPException(status_code=500, detail="Erro ao gerar o PDF.")