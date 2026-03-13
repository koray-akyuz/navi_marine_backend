from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from models.reports import FishReport
from schemas.reports import FishReportCreate, FishReportResponse
from schemas.spatial import MapBounds
from services.weather import get_marine_weather

router = APIRouter()

@router.post("/", response_model=FishReportResponse)
async def create_fish_report(report_in: FishReportCreate, db: AsyncSession = Depends(get_db)):
    # 1. Lokasyon Doğrulaması (Buffer kullanarak)
    check_query = text("""
        SELECT EXISTS (
            SELECT 1 FROM sea_areas 
            WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 0.002)
        )
    """)
    res = await db.execute(check_query, {"lat": report_in.latitude, "lon": report_in.longitude})
    if not res.scalar():
        raise HTTPException(status_code=400, detail="Kaptan, karada balık raporlayamazsın!")

    # 2. Rapor anındaki hava durumunu çek (Historical Weather)
    weather = await get_marine_weather(report_in.latitude, report_in.longitude)

    # 3. Veritabanına Kayıt
    point_wkt = f"SRID=4326;POINT({report_in.longitude} {report_in.latitude})"
    
    new_report = FishReport(
        fish_type_id = report_in.fish_type_id,
        latitude     = report_in.latitude,
        longitude    = report_in.longitude,
        note         = report_in.note,
        geom         = point_wkt,
        # Hava durumu — alınamazsa None (nullable)
        wind_speed   = weather.get("wind_speed")  if weather else None,
        wind_deg     = weather.get("wind_deg")    if weather else None,
        wind_name    = weather.get("wind_name")   if weather else None,
        temperature  = weather.get("temp")        if weather else None,
    )
    
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report


@router.post("/nearby", response_model=list[FishReportResponse])
async def get_nearby_reports(bounds: MapBounds, db: AsyncSession = Depends(get_db)):
    """
    Haritadaki görünür alan (BBox) içindeki balık raporlarını getirir.
    DB bağlantısı yoksa boş liste döner (uygulama çökmez).
    """
    try:
        query = text("""
            SELECT id, fish_type_id, latitude, longitude, note, created_at, updated_at,
                   wind_speed, wind_deg, wind_name, temperature
            FROM fish_reports
            WHERE geom && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
            LIMIT 200
        """)
        result = await db.execute(query, {
            "min_lon": bounds.min_lon,
            "min_lat": bounds.min_lat,
            "max_lon": bounds.max_lon,
            "max_lat": bounds.max_lat
        })
        return result.fetchall()
    except Exception:
        # DB çalışmıyorsa sessizce boş liste döndür
        return []

@router.get("/{report_id}", response_model=FishReportResponse)
async def get_report_detail(report_id: int, db: AsyncSession = Depends(get_db)):
    """
    Spesifik bir raporun detaylarını (hava durumu dahil) getirir.
    """
    report = await db.get(FishReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı.")
    return report