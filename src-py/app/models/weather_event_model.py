from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class WeatherEvent(Base):
    __tablename__ = "weather_events"

    id = Column(Integer, primary_key=True, index=True)
    journey_id = Column(Integer, ForeignKey("journeys.id"), nullable=True)
    
    # Detalhes do Evento
    event_type = Column(String) # Ex: "Thunderstorm", "Snow", "Fog"
    severity = Column(String)   # Ex: "Severe", "Moderate"
    description = Column(String)
    
    # Geometria da área afetada (Círculo ou Polígono aproximado)
    affected_lat = Column(Float)
    affected_lon = Column(Float)
    affected_radius_km = Column(Float, default=10.0) # Raio de impacto
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)

    # Relacionamentos
    journey = relationship("Journey", backref="weather_events")