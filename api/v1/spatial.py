from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_db
from schemas.spatial import CoordinateCheck

router = APIRouter()

@router.post("/validate-location")
async def validate_location(coord: CoordinateCheck, db: AsyncSession = Depends(get_db)):
    """
    Koordinatın denizde olup olmadığını PostGIS ile kontrol eder.
    """
    # ST_Contains veya ST_Intersects kullanabiliriz. 
    # ST_SetSRID ile noktanın koordinat sistemini (4326 - WGS84) belirtiyoruz.
    query = text("""
        SELECT EXISTS (
            SELECT 1 
            FROM sea_areas 
            WHERE ST_DWithin(
                geom, 
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                0.005
            )
        )
    """)
    
    result = await db.execute(query, {"lat": coord.latitude, "lon": coord.longitude})
    is_in_sea = result.scalar()

    if not is_in_sea:
        return {
            "is_valid": False, 
            "message": "Kaptan, karadasın! Balık raporu için denize açılmalısın."
        }
    
    return {"is_valid": True, "message": "Rastgele! Denizdesin."}