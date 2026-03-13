from sqlalchemy import func, select
from geoalchemy2.functions import ST_Intersects
from sqlalchemy.ext.asyncio import AsyncSession
from models.spatial import SeaArea

async def validate_fishing_spot(db: AsyncSession, lat: float, lon: float):
    # Kullanıcının tıkladığı noktayı PostGIS formatına (WKT) çevir
    point = f'SRID=4326;POINT({lon} {lat})'
    
    # ST_Intersects: Nokta poligonun içinde mi?
    query = await db.execute(
        select(SeaArea).filter(ST_Intersects(SeaArea.geom, point))
    )
    
    result = query.scalars().first()
    return result is not None
