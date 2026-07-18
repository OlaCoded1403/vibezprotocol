# ================================================================
#  VIBEZ PROTOCOL — app/routes/auth.py
# ================================================================

import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import AdminUser
from app.schemas import LoginRequest, TokenResponse, MessageResponse
from app.utils import verify_password, hash_password, create_access_token

load_dotenv()

router       = APIRouter()
SETUP_SECRET = os.getenv("SETUP_SECRET", "vibez-setup-2025")


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token(data={"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/setup", response_model=MessageResponse)
async def setup_admin(
    payload:   LoginRequest,
    setup_key: str,
    db:        Session = Depends(get_db),
):
    """
    ONE-TIME setup. Run this once after first launch to create your admin account.
    URL:  POST /api/auth/setup?setup_key=YOUR_SETUP_SECRET
    Body: { "username": "olamilekan", "password": "yourpassword" }
    """
    if setup_key != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid setup key")
    existing = db.query(AdminUser).filter(AdminUser.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists. Go to /admin to log in.")
    admin = AdminUser(
        username      = payload.username,
        password_hash = hash_password(payload.password),
    )
    db.add(admin)
    db.commit()
    return {"message": f"Admin '{payload.username}' created. Log in at /admin"}
