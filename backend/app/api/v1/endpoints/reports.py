from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from datetime import datetime, timedelta

from app.api import deps
from app.schemas.report_schema import DashboardSummary
from app.models.user_model import User

router = APIRouter()

@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary_data(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager), # Garante que apenas gestores acedam
):
    """
    Retorna os dados agregados para o dashboard do gestor.
    """
    # CORREÇÃO 1: A variável é definida DENTRO do corpo da função, não nos parâmetros.
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # CORREÇÃO 2: Passamos a data e o utilizador para a função de cálculo no CRUD.
    # Isto permite que o CRUD filtre os dados pela organização do gestor e pelo período de tempo.
    summary_data = await crud.report.get_dashboard_summary(
        db, 
        current_user=current_user, 
        start_date=thirty_days_ago
    )
    
    return summary_data