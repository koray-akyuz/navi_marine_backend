from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from typing import List

from database import get_db
from models import FishReportLike, FishReportComment, User, FishReport
from schemas.social import LikeCreate, CommentCreate, CommentResponse
from api.v1.deps import get_current_user

router = APIRouter()

# --- LIKES ---
@router.post("/like/{report_id}")
async def like_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Bir raporu beğenir veya beğeniyi geri çeker (Toggle).
    """
    # Rapor var mı kontrol et
    report = await db.get(FishReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı.")

    # Zaten beğenmiş mi?
    stmt = select(FishReportLike).where(
        FishReportLike.user_id == current_user.id,
        FishReportLike.report_id == report_id
    )
    result = await db.execute(stmt)
    existing_like = result.scalar_one_or_none()

    if existing_like:
        await db.delete(existing_like)
        await db.commit()
        return {"liked": False, "message": "Beğeni geri çekildi."}
    else:
        new_like = FishReportLike(user_id=current_user.id, report_id=report_id)
        db.add(new_like)
        await db.commit()
        return {"liked": True, "message": "Rapor beğenildi."}

# --- COMMENTS ---
@router.get("/comments/{report_id}", response_model=List[CommentResponse])
async def get_comments(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Bir rapora yapılan yorumları getirir.
    """
    stmt = select(FishReportComment).where(
        FishReportComment.report_id == report_id
    ).order_by(FishReportComment.created_at.asc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Yeni bir yorum yapar.
    """
    # Rapor var mı kontrol et
    report = await db.get(FishReport, comment_in.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı.")

    new_comment = FishReportComment(
        user_id=current_user.id,
        report_id=comment_in.report_id,
        content=comment_in.content
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    
    # User bilgisini preload et
    stmt = select(FishReportComment).where(FishReportComment.id == new_comment.id)
    result = await db.execute(stmt)
    return result.scalar_one()

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Yorumu siler.
    """
    comment = await db.get(FishReportComment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı.")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sadece kendi yorumunuzu silebilirsiniz.")
    
    await db.delete(comment)
    await db.commit()
    return {"message": "Yorum silindi."}
