from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    nickname: str
    name: str
    surname: str
    city: Optional[str] = None
    district: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    nickname: str
    password: str

class GoogleLogin(BaseModel):
    id_token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    nickname: str
    user_id: int

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True
