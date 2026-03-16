from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from schemas.spatial import CoordinateCheck, RouteCheck

router = APIRouter()

@router.post("/validate-route")
async def validate_route(route: RouteCheck, db: AsyncSession = Depends(get_db)):
    """
    İki nokta arasındaki kuş uçuşu rotanın karadan geçip geçmediğini kontrol eder.
    """
    query = text("""
        SELECT EXISTS (
            SELECT 1 
            FROM land_areas 
            WHERE ST_Intersects(
                geom, 
                ST_MakeLine(
                    ST_SetSRID(ST_MakePoint(:lon1, :lat1), 4326),
                    ST_SetSRID(ST_MakePoint(:lon2, :lat2), 4326)
                )
            )
        )
    """)
    
    try:
        result = await db.execute(query, {
            "lat1": route.lat1, "lon1": route.lon1,
            "lat2": route.lat2, "lon2": route.lon2
        })
        crosses_land = result.scalar()
    except Exception:
        # land_areas yoksa veya hata oluşursa güvenli tarafta kal (onay verme demiyoruz ama false da dönmeyebiliriz)
        crosses_land = False

    if crosses_land:
        return {
            "is_valid": False, 
            "message": "Dikkat Kaptan! Bu rota karadan geçiyor. Fatih Sultan Mehmet gibi gemileri karadan yürütmeyelim!"
        }
    
    return {"is_valid": True, "message": "Rota güvenli görünüyor."}


@router.post("/validate-location")
async def validate_location(coord: CoordinateCheck, db: AsyncSession = Depends(get_db)):
    """
    Koordinatın denizde olup olmadığını kontrol eder.
    Mantık: OSM land_areas (kara maskesi) tablosuna bakar. 
    Eğer nokta karada DEĞİLSE, denizde kabul edilir.
    """
    # 100 metrelik bir pay (0.001 derece) bırakıyoruz.
    query = text("""
        SELECT NOT EXISTS (
            SELECT 1 
            FROM land_areas 
            WHERE ST_DWithin(
                geom, 
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                0.001
            )
        )
    """)
    
    try:
        result = await db.execute(query, {"lat": coord.latitude, "lon": coord.longitude})
        is_in_sea = result.scalar()
    except Exception:
        # land_areas tablosu henüz yoksa (fail-safe) eski sea_areas mantığına fallback yap
        fallback_query = text("""
            SELECT EXISTS (
                SELECT 1 FROM sea_areas 
                WHERE ST_DWithin(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 0.02)
            )
        """)
        result = await db.execute(fallback_query, {"lat": coord.latitude, "lon": coord.longitude})
        is_in_sea = result.scalar()

    if not is_in_sea:
        return {
            "is_valid": False, 
            "message": "Kaptan, karadasın! Balık raporu veya seyir için denize açılmalısın."
        }
    
    return {"is_valid": True, "message": "Rastgele! Denizdesin."}