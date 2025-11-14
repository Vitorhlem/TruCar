from pydantic import BaseModel
from typing import List, Optional

class DriverPerformance(BaseModel):
    user_id: int
    full_name: str
    performance_score: float 
    avg_km_per_liter: float
    total_km_driven: float
    maintenance_requests_count: int
    avatar_url: Optional[str] = None # Adicionado


class LeaderboardResponse(BaseModel):
    leaderboard: List[DriverPerformance]