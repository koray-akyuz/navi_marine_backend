from pydantic import BaseModel, Field, AliasChoices
from typing import List, Optional
from datetime import datetime

class TrackCreate(BaseModel):
    name: Optional[str] = None
    # Hem 'points' (API request) hem 'points_json' (DB response) ismini kabul et
    points: List[dict] = Field(..., validation_alias=AliasChoices('points', 'points_json'), serialization_alias='points')
    distance: Optional[float] = None
    duration: Optional[int] = None

class TrackResponse(TrackCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
