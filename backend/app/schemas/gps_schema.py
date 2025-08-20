from pydantic import BaseModel

class LocationCreate(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float