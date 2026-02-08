from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Project
from ..schemas import ProjectCreate, ProjectPatch, ProjectRead, to_read

router = APIRouter(prefix="/projects", tags=["projects"])


def _get_by_id(db: Session, project_id: int) -> Project | None:
    if hasattr(db, "get"):
        return db.get(Project, project_id)
    return db.query(Project).get(project_id)


@router.get("/", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    rows = db.query(Project).order_by(Project.created_at.desc()).all()
    return [to_read(ProjectRead, row) for row in rows]


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    db.flush()
    db.refresh(project)
    return to_read(ProjectRead, project)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectRead:
    project = _get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return to_read(ProjectRead, project)


@router.patch("/{project_id}", response_model=ProjectRead)
def patch_project(
    project_id: int, payload: ProjectPatch, db: Session = Depends(get_db)
) -> ProjectRead:
    project = _get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    db.add(project)
    db.flush()
    db.refresh(project)
    return to_read(ProjectRead, project)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> Response:
    project = _get_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.flush()
    return Response(status_code=204)
