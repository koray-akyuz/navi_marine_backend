from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services import validate_fishing_spot
from pydantic import BaseModel
from datetime import datetime
from typing import List
from sqlalchemy import func
from models.spatial import SeaArea
from database import get_db
import uvicorn
from api.v1 import spatial as api_v1_router
from api.v1 import reports as api_v1_reports_router
from api.v1 import weather as api_v1_weather_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Vira Bismillah API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FishReportCreate(BaseModel):
    fish_type_id: str
    latitude: float
    longitude: float
    note: str = None

app.include_router(api_v1_router.router, prefix="/api/v1/spatial")
app.include_router(api_v1_reports_router.router, prefix="/api/v1/reports")
app.include_router(api_v1_weather_router.router, prefix="/api/v1/weather")

@app.post("/reports/")
async def create_report(report: FishReportCreate):
    # Burada koordinatlar PostGIS'e kaydedilecek: 
    # ST_SetSRID(ST_MakePoint(lon, lat), 4326)
    return {"status": "success", "message": "Rapor ağa takıldı!"}

@app.get("/reports/nearby")
async def get_nearby_reports(lat: float, lon: float, radius: int = 5000):
    # Belirli bir yarıçaptaki balıkları dönen query:
    # ST_DWithin(geom, ST_MakePoint(lon, lat), radius)
    return []

@app.get("/check-sea")
async def is_it_sea(lat: float, lon: float, db: AsyncSession = Depends(get_db)):
    return await validate_fishing_spot(db, lat, lon)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)