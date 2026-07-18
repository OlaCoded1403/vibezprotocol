# ================================================================
#  VIBEZ PROTOCOL — app/schemas.py
#  Pydantic request/response validation schemas
# ================================================================

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ── CONTACT ──────────────────────────────────────────────────────
class InquiryCreate(BaseModel):
    name:    str
    email:   EmailStr
    subject: str
    message: str

    @field_validator("name", "subject", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class InquiryResponse(BaseModel):
    id:         int
    name:       str
    email:      str
    subject:    str
    message:    str
    is_read:    bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── PROJECTS ──────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    title:       str
    category:    str
    description: str
    tags:        Optional[str]  = None
    url:         Optional[str]  = None
    image_url:   Optional[str]  = None
    is_featured: Optional[bool] = False
    is_visible:  Optional[bool] = True


class ProjectUpdate(BaseModel):
    title:       Optional[str]  = None
    category:    Optional[str]  = None
    description: Optional[str]  = None
    tags:        Optional[str]  = None
    url:         Optional[str]  = None
    image_url:   Optional[str]  = None
    is_featured: Optional[bool] = None
    is_visible:  Optional[bool] = None


class ProjectResponse(BaseModel):
    id:          int
    title:       str
    category:    str
    description: str
    tags:        Optional[str]
    url:         Optional[str]
    image_url:   Optional[str]
    is_featured: bool
    is_visible:  bool
    created_at:  datetime

    class Config:
        from_attributes = True


# ── AUTH ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── GENERIC ───────────────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str
