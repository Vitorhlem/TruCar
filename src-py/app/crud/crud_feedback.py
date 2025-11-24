from sqlalchemy.ext.asyncio import AsyncSession
from app.models.feedback_model import Feedback
from app.schemas.feedback_schema import FeedbackCreate

async def create_feedback(
    db: AsyncSession, feedback_in: FeedbackCreate, user_id: int, organization_id: int
) -> Feedback:
    db_obj = Feedback(
        type=feedback_in.type,
        message=feedback_in.message,
        user_id=user_id,
        organization_id=organization_id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj