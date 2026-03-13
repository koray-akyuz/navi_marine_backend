from fastapi import APIRouter, HTTPException
from services.weather import get_weather_data, get_marine_weather, get_wind_grid

router = APIRouter()

@router.get("/analyze")
async def analyze_weather(lat: float, lon: float):
    weather = await get_weather_data(lat, lon)
    if not weather:
        raise HTTPException(status_code=404, detail="Hava durumu verisi alınamadı")
    
    # Basit bir balıkçılık algoritması
    is_safe = weather["wind_speed"] < 8.0 # 8 m/s üstü tehlikeli olabilir
    pressure_trend = "Yüksek" if weather["pressure"] > 1013 else "Alçak"
    
    return {
        "current": weather,
        "advice": "Denize çıkış uygun" if is_safe else "Dikkat: Sert rüzgar!",
        "pressure_status": pressure_trend
    }

@router.get("/weather")
async def get_weather(lat: float, lon: float):
    weather = await get_marine_weather(lat, lon)
    if not weather:
        raise HTTPException(status_code=404, detail="Hava durumu verisi alınamadı")
    
    # Basit bir balıkçılık algoritması
    is_safe = weather["wind_speed"] < 8.0 # 8 m/s üstü tehlikeli olabilir
    pressure_trend = "Yüksek" if weather["pressure"] > 1013 else "Alçak"
    
    return {
        "current": weather,
        "advice": "Denize çıkış uygun" if is_safe else "Dikkat: Sert rüzgar!",
        "pressure_status": pressure_trend
    }

@router.get("/wind-grid")
async def get_wind_grid_endpoint(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    steps: int = 5
):
    grid = await get_wind_grid(min_lat, max_lat, min_lon, max_lon, steps)
    if grid is None:
        raise HTTPException(status_code=503, detail="Rüzgar ızgara verisi alınamadı")
    return grid