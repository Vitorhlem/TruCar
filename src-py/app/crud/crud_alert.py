from sqlalchemy.ext.asyncio import AsyncSession
from app.models.alert_model import Alert
from app.schemas.alert_schema import AlertCreate
from typing import Union, Dict, Any

class CRUDAlert:
    async def create(self, db: AsyncSession, obj_in: Union[AlertCreate, Dict[str, Any]]) -> Alert:
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        db_obj = Alert(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

alert = CRUDAlert()