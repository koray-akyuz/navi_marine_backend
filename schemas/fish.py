from pydantic import BaseModel
from typing import Optional

class FishTypeBase(BaseModel):
    slug: str
    name: str
    icon_url: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class FishTypeCreate(FishTypeBase):
    pass

class FishTypeResponse(FishTypeBase):
    id: int

    class Config:
        from_attributes = True
