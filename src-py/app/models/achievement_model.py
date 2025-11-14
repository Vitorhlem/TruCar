from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Achievement(Base):
    """Define uma conquista que pode ser desbloqueada."""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False) # Ex: 'SAFE_DRIVER_30_DAYS'
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=False) # Ex: 'health_and_safety'

class UserAchievement(Base):
    """Tabela de ligação que registra qual motorista desbloqueou qual conquista."""
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement")

    __table_args__ = (UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),)
