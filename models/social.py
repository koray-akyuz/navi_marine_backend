from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import AppBase

class FishReportLike(AppBase):
    __tablename__ = "fish_report_likes"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("fish_reports.id"), nullable=False)
    
    user = relationship("User")
    report = relationship("FishReport")

class FishReportComment(AppBase):
    __tablename__ = "fish_report_comments"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("fish_reports.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    report = relationship("FishReport")

class SOSAlarm(AppBase):
    __tablename__ = "sos_alarms"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User")
