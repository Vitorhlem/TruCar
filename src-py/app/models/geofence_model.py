from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey
from app.db.base_class import Base

class Geofence(Base):
    __tablename__ = "geofences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # Ex: "Garagem Central"
    type = Column(String, default="SAFE_ZONE") # SAFE_ZONE, RISK_ZONE, CUSTOMER
    
    # Armazena a lista de coordenadas: [[lat, lon], [lat, lon], ...]
    polygon_points = Column(JSON, nullable=False) 
    
    color = Column(String, default="#4caf50") # Verde para seguro, Vermelho para risco
    is_active = Column(Boolean, default=True)
    
    # Se quiser vincular a uma empresa/organização
    # organization_id = Column(Integer, ForeignKey("organizations.id"))