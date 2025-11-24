from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert_model import Alert
from app.schemas.alert_schema import AlertCreate

class CRUDAlert:
    async def create(self, db: AsyncSession, obj_in: AlertCreate) -> Alert:
        db_obj = Alert(
            message=obj_in.message,
            level=obj_in.level,
            organization_id=obj_in.organization_id,
            vehicle_id=obj_in.vehicle_id,
            driver_id=obj_in.driver_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

alert = CRUDAlert()