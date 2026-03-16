from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from typing import List
from datetime import datetime

from database import get_db
from models import SOSAlarm, User
from schemas.social import SOSCreate, SOSResponse
from api.v1.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=SOSResponse)
async def create_sos(
    sos_in: SOSCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Acil durum (SOS) alarmı oluşturur.
    """
    new_sos = SOSAlarm(
        user_id=current_user.id,
        latitude=sos_in.latitude,
        longitude=sos_in.longitude,
        message=sos_in.message,
        is_active=True
    )
    db.add(new_sos)
    await db.commit()
    await db.refresh(new_sos)
    
    # User bilgisini preload et
    stmt = select(SOSAlarm).options(joinedload(SOSAlarm.user)).where(SOSAlarm.id == new_sos.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@router.get("/active", response_model=List[SOSResponse])
async def get_active_sos(db: AsyncSession = Depends(get_db)):
    """
    Tüm aktif SOS alarmlarını getirir.
    """
    stmt = select(SOSAlarm).options(joinedload(SOSAlarm.user)).where(SOSAlarm.is_active == True).order_by(SOSAlarm.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{sos_id}/resolve")
async def resolve_sos(
    sos_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    SOS alarmını çözümlendi (pasif) olarak işaretler.
    Sadece alarmı açan kullanıcı veya admin (ileride) yapabilir.
    """
    stmt = select(SOSAlarm).where(SOSAlarm.id == sos_id)
    result = await db.execute(stmt)
    sos = result.scalar_one_or_none()
    
    if not sos:
        raise HTTPException(status_code=404, detail="SOS alarmı bulunamadı.")
    
    if sos.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Bu işlemi yapmak için yetkiniz yok.")
    
    sos.is_active = False
    sos.resolved_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "SOS alarmı çözümlendi."}
