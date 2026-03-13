from sqlalchemy import Column, String, Float, Text, ForeignKey
from geoalchemy2 import Geometry
from .base import AppBase

class FishReport(AppBase):
    __tablename__ = "fish_reports"

    # Balık türü (Örn: 'levrek', 'cipura')
    fish_type_id = Column(String(50), nullable=False, index=True)
    
    # Kullanıcı notu (Opsiyonel)
    note = Column(Text, nullable=True)
    
    # Koordinatı Point (Nokta) geometrisi olarak saklıyoruz (SRID 4326 = WGS84)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    # Ham koordinatlar
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # --- Rapor anındaki hava durumu (Historical Weather) ---
    wind_speed  = Column(Float,        nullable=True)   # knot
    wind_deg    = Column(Float,        nullable=True)   # 0-360 derece
    wind_name   = Column(String(50),   nullable=True)   # 'Poyraz', 'Lodos' vs.
    temperature = Column(Float,        nullable=True)   # °C