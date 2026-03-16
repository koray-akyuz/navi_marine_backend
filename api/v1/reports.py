from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from models.reports import FishReport
from schemas.reports import FishReportCreate, FishReportResponse
from schemas.spatial import MapBounds
from services.weather import get_marine_weather
from api.v1.deps import get_current_user
from models.users import User
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/", response_model=FishReportResponse)
async def create_fish_report(
    report_in: FishReportCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
        user_id      = current_user.id
    )
    
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report


@router.get("/me", response_model=list[FishReportResponse])
async def get_my_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Giriş yapmış kullanıcının kendi raporlarını getirir.
    """
    query = select(FishReport).where(FishReport.user_id == current_user.id).order_by(FishReport.created_at.desc())
    result = await db.execute(query)
    reports = result.scalars().all()
    
    for r in reports:
        r.reporter_nickname = current_user.nickname
        
    return reports

@router.post("/nearby", response_model=list[FishReportResponse])
async def get_nearby_reports(bounds: MapBounds, db: AsyncSession = Depends(get_db)):
    """
    Haritadaki görünür alan (BBox) içindeki balık raporlarını getirir.
    DB bağlantısı yoksa boş liste döner (uygulama çökmez).
    """
    try:
        query = text("""
            SELECT r.id, r.fish_type_id, r.latitude, r.longitude, r.note, r.created_at, r.updated_at,
                   r.wind_speed, r.wind_deg, r.wind_name, r.temperature,
                   u.nickname as reporter_nickname
            FROM fish_reports r
            LEFT JOIN users u ON r.user_id = u.id
            WHERE r.geom && ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
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
    query = select(FishReport).options(joinedload(FishReport.reporter)).where(FishReport.id == report_id)
    result = await db.execute(query)
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı.")
    
    # reporter_nickname field'ını doldur (ResponseSchema için)
    if report.reporter:
        report.reporter_nickname = report.reporter.nickname
        
    return report