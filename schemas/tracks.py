from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TrackCreate(BaseModel):
    name: Optional[str] = None
    points: List[dict] # [{"latitude": 1.2, "longitude": 3.4}, ...]
    distance: Optional[float] = None
    duration: Optional[int] = None

class TrackResponse(TrackCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
