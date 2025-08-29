# ARQUIVO: backend/app/api/v1/endpoints/leaderboard.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user_model import User
from app.schemas.user_schema import LeaderboardResponse

router = APIRouter()

@router.get("/", response_model=LeaderboardResponse)
async def read_leaderboard(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """
    Retorna os dados do placar de líderes para a organização do usuário logado.
    """
    leaderboard_data = await crud.user.get_leaderboard_data(
        db, organization_id=current_user.organization_id
    )
    return leaderboard_data