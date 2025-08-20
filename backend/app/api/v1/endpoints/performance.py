from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.performance_schema import LeaderboardResponse

router = APIRouter()

@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard_data(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_manager),
):
    """
    Retorna o ranking de performance dos motoristas. Acessível apenas para gestores.
    """
    leaderboard_data = await crud.report.get_driver_leaderboard(db, organization_id=current_user.organization_id)
    return leaderboard_data