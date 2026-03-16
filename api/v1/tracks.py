from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.tracks import Track
from schemas.tracks import TrackCreate, TrackResponse
from typing import List

from api.v1.deps import get_current_user
from models.users import User

router = APIRouter()

@router.post("/", response_model=TrackResponse)
async def create_track(
    track_in: TrackCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Points listesini WKT formatına çevirme (LINESTRING(lon1 lat1, lon2 lat2, ...))
    try:
        wkt_points = ", ".join([f"{p['longitude']} {p['latitude']}" for p in track_in.points])
        wkt_linestring = f"LINESTRING({wkt_points})"
        
        new_track = Track(
            user_id=current_user.id,
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
async def get_user_tracks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Sadece giriş yapmış kullanıcının track'lerini getir
    query = select(Track).where(Track.user_id == current_user.id).order_by(Track.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
