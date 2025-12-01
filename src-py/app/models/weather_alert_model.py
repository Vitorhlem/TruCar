# Exemplo conceitual usando SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from app.db.base_class import Base
from sqlalchemy.sql.sqltypes import Boolean

class WeatherEvent(Base):
    __tablename__ = "weather_events"
    
    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journey.id")) # Vincula à jornada afetada
    severity = Column(String) # "Severe", "Moderate"
    event_type = Column(String) # "Storm", "Tornado", "Flood"
    affected_area_polygon = Column(JSON) # GeoJSON do polígono da tempestade
    description = Column(String)
    detected_at = Column(DateTime)
    is_active = Column(Boolean, default=True)