from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBasic(BaseModel):
    id: int
    nickname: str

    class Config:
        from_attributes = True

# --- LIKES ---
class LikeBase(BaseModel):
    report_id: int

class LikeCreate(LikeBase):
    pass

# --- COMMENTS ---
class CommentBase(BaseModel):
    report_id: int
    content: str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int
    user_id: int
    user: UserBasic
    created_at: datetime

    class Config:
        from_attributes = True

# --- SOS ---
class SOSBase(BaseModel):
    latitude: float
    longitude: float
    message: Optional[str] = None

class SOSCreate(SOSBase):
    pass

class SOSResponse(SOSBase):
    id: int
    user_id: int
    user: UserBasic
    is_active: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
