from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from database import get_db
from models.fish import FishType
from schemas.fish import FishTypeResponse

router = APIRouter()

@router.get("/", response_model=List[FishTypeResponse])
async def get_fish_types(db: AsyncSession = Depends(get_db)):
    """
    Sisteme kayıtlı tüm balık türlerini döner.
    """
    query = select(FishType).order_by(FishType.name)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/seed")
async def seed_fish_types(db: AsyncSession = Depends(get_db)):
    """
    Başlangıç balık türlerini veritabanına ekler.
    """
    initial_fish = [
        {"slug": "cipura", "name": "Çipura", "color": "#f1c40f", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/cipura.png"},
        {"slug": "levrek", "name": "Levrek", "color": "#3498db", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/levrek.png"},
        {"slug": "lufer", "name": "Lüfer", "color": "#e74c3c", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/lufer.png"},
        {"slug": "istavrit", "name": "İstavrit", "color": "#95a5a6", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/istavrit.png"},
        {"slug": "palamut", "name": "Palamut", "color": "#2c3e50", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/palamut.png"},
        {"slug": "mercan", "name": "Mercan", "color": "#ff7f50", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/mercan.png"},
        {"slug": "mirmir", "name": "Mırmır", "color": "#bdc3c7", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/mirmir.png"},
        {"slug": "karagoz", "name": "Karagöz", "color": "#34495e", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/karagoz.png"},
        {"slug": "kalkan", "name": "Kalkan", "color": "#d35400", "icon_url": "https://raw.githubusercontent.com/lucidmot/navi-marine-assets/main/kalkan.png"},
    ]
    
    for f_data in initial_fish:
        query = select(FishType).where(FishType.slug == f_data["slug"])
        res = await db.execute(query)
        if not res.scalar():
            db.add(FishType(**f_data))
            
    await db.commit()
    return {"status": "success", "message": "Balıklar limana yanaştı!"}
