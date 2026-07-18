# ================================================================
#  VIBEZ PROTOCOL — app/routes/projects.py
# ================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.utils import get_current_admin

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    return (
        db.query(Project)
        .filter(Project.is_visible == True)
        .order_by(Project.is_featured.desc(), Project.created_at.desc())
        .all()
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload:  ProjectCreate,
    db:       Session = Depends(get_db),
    _:        str     = Depends(get_current_admin),
):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    payload:    ProjectUpdate,
    db:         Session = Depends(get_db),
    _:          str     = Depends(get_current_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db:         Session = Depends(get_db),
    _:          str     = Depends(get_current_admin),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
