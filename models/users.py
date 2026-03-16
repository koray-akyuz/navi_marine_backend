from sqlalchemy import Column, String
from .base import AppBase

class User(AppBase):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)   # SHA256 hashed, null if Google Login
    city = Column(String, nullable=True)       # il
    district = Column(String, nullable=True)   # ilce
