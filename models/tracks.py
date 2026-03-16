from sqlalchemy import Column, String, Float, ForeignKey, Integer, JSON
from geoalchemy2 import Geometry
from .base import AppBase
from sqlalchemy.orm import relationship

class Track(AppBase):
    __tablename__ = "tracks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author = relationship("User")

    name = Column(String(100), nullable=True)
    
    # Haritadaki çizim için LineString geometrisi
    geom = Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=False)
    
    # Tüm koordinatları JSON liste olarak da saklayalım (Frontend kolaylığı için)
    # [{"latitude": ..., "longitude": ...}, ...]
    points_json = Column(JSON, nullable=False)
    
    distance = Column(Float, nullable=True) # nm
    duration = Column(Integer, nullable=True) # saniye
