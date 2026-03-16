from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FishReportCreate(BaseModel):
    fish_type_id: str = Field(..., example="levrek")
    latitude:     float = Field(..., ge=-90,  le=90)
    longitude:    float = Field(..., ge=-180, le=180)
    note:         Optional[str]   = None
    # Hava durumu backend tarafından doldurulur; frontend de gönderebilir
    wind_speed:   Optional[float] = None
    wind_deg:     Optional[float] = None
    wind_name:    Optional[str]   = None
    temperature:  Optional[float] = None

class FishReportResponse(FishReportCreate):
    id:           int
    created_at:   datetime
    updated_at:   Optional[datetime] = None
    wind_speed:   Optional[float]    = None
    wind_deg:     Optional[float]    = None
    wind_name:    Optional[str]      = None
    temperature:  Optional[float]    = None
    reporter_nickname: Optional[str] = None
    likes_count:       int = 0
    comments_count:    int = 0

    class Config:
        from_attributes = True