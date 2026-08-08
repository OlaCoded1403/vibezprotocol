# ================================================================
#  VIBEZ PROTOCOL — app/main.py
#  Author: Oyeyemi Olamilekan
#  FastAPI Backend — Entry Point
# ================================================================

import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import contact, projects, admin, auth

# Windows consoles default to cp1252 when stdout is piped, and the emoji in our
# startup logs raise UnicodeEncodeError there — which would kill the app on boot.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ Vibez Protocol API is live")
    yield
    print("👋 Server shutting down")


app = FastAPI(
    title="Vibez Protocol API",
    description="Backend for Vibez Protocol — AI Engineering Studio by Oyeyemi Olamilekan",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────
# Only the frontend origins need access. /admin is served by this same app,
# so it is same-origin and needs no entry here.
# Override with an ALLOWED_ORIGINS env var (comma-separated) when the domain
# changes — no code edit and no redeploy of the frontend required.
DEFAULT_ORIGINS = ",".join([
    "https://vibezprotocol.onrender.com",
    "http://localhost:5501",       # VSCode Live Server
    "http://127.0.0.1:5501",
])
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/api/auth",     tags=["Auth"])
app.include_router(contact.router,  prefix="/api/contact",  tags=["Contact"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(admin.router,    prefix="/api/admin",    tags=["Admin"])

# ── Admin dashboard static files ─────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return FileResponse("static/admin.html")

# ── Health check ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "live",
        "project": "Vibez Protocol API",
        "version": "1.0.0",
        "docs": "/docs",
    }
