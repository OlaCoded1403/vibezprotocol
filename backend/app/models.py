# ================================================================
#  VIBEZ PROTOCOL — app/models.py
#  Database table definitions
# ================================================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Inquiry(Base):
    """Contact form submissions from the website."""
    __tablename__ = "inquiries"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), nullable=False)
    subject    = Column(String(200), nullable=False)
    message    = Column(Text, nullable=False)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Project(Base):
    """Portfolio projects — manageable from the admin dashboard."""
    __tablename__ = "projects"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    category    = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    tags        = Column(String(500), nullable=True)   # comma-separated
    url         = Column(String(500), nullable=True)   # live project link
    image_url   = Column(String(500), nullable=True)   # screenshot
    is_featured = Column(Boolean, default=False)
    is_visible  = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class AdminUser(Base):
    """Admin login — Oyeyemi Olamilekan only."""
    __tablename__ = "admin_users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
