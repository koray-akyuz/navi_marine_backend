from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from database import Base
from sqlalchemy import func

class TimestampModel:
    """Oluşturulma ve güncellenme tarihlerini otomatik tutar"""
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now())
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now())

class AppBase(Base, TimestampModel):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)