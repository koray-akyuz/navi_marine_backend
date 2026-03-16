from sqlalchemy import Column, String, Text
from .base import AppBase

class FishType(AppBase):
    __tablename__ = "fish_types"

    # Slug-like ID (e.g., 'cipura', 'levrek')
    slug = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    icon_url = Column(String(255), nullable=True)  # URL to the thumbnail
    color = Column(String(7), nullable=True)     # Hex color code (e.g., '#f1c40f')
    description = Column(Text, nullable=True)
