# ================================================================
#  VIBEZ PROTOCOL — app/routes/admin.py
# ================================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Inquiry, Project
from app.schemas import InquiryResponse, MessageResponse
from app.utils import get_current_admin

router = APIRouter()


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    _:  str     = Depends(get_current_admin),
):
    return {
        "total_inquiries":  db.query(Inquiry).count(),
        "unread_inquiries": db.query(Inquiry).filter(Inquiry.is_read == False).count(),
        "total_projects":   db.query(Project).count(),
        "visible_projects": db.query(Project).filter(Project.is_visible == True).count(),
    }


@router.get("/inquiries", response_model=List[InquiryResponse])
async def get_inquiries(
    db: Session = Depends(get_db),
    _:  str     = Depends(get_current_admin),
):
    return db.query(Inquiry).order_by(Inquiry.created_at.desc()).all()


@router.put("/inquiries/{inquiry_id}/read", response_model=MessageResponse)
async def mark_read(
    inquiry_id: int,
    db:         Session = Depends(get_db),
    _:          str     = Depends(get_current_admin),
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    inquiry.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.delete("/inquiries/{inquiry_id}", response_model=MessageResponse)
async def delete_inquiry(
    inquiry_id: int,
    db:         Session = Depends(get_db),
    _:          str     = Depends(get_current_admin),
):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    db.delete(inquiry)
    db.commit()
    return {"message": "Inquiry deleted"}
