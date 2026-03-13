from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from .database import Base

class SeaArea(Base):
    __tablename__ = "sea_areas"
    id = Column(Integer, primary_key=True)
    # 'GEOMETRY' tipi sayesinde tüm deniz sınırlarını burada tutuyoruz
    geom = Column(Geometry('POLYGON', srid=4326))