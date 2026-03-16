from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.tracks import Track
from schemas.tracks import TrackCreate, TrackResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=TrackResponse)
async def create_track(track_in: TrackCreate, db: AsyncSession = Depends(get_db)):
    # Points listesini WKT formatına çevirme (LINESTRING(lon1 lat1, lon2 lat2, ...))
    # NOT: PostGIS'te genellikle LON-LAT sırası kullanılır.
    try:
        wkt_points = ", ".join([f"{p['longitude']} {p['latitude']}" for p in track_in.points])
        wkt_linestring = f"LINESTRING({wkt_points})"
        
        new_track = Track(
            name=track_in.name,
            points_json=track_in.points,
            distance=track_in.distance,
            duration=track_in.duration,
            geom=f"SRID=4326;{wkt_linestring}"
        )
        
        db.add(new_track)
        await db.commit()
        await db.refresh(new_track)
        return new_track
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Track kaydedilemedi: {str(e)}")

@router.get("/", response_model=List[TrackResponse])
async def get_user_tracks(db: AsyncSession = Depends(get_db)):
    # AsyncSession ile select kullanımı
    result = await db.execute(select(Track).order_by(Track.created_at.desc()))
    return result.scalars().all()
