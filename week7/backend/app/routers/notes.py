from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Project
from ..schemas import NoteCreate, NotePatch, NoteRead, to_read

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_by_id(db: Session, model, item_id: int):
    if hasattr(db, "get"):
        return db.get(model, item_id)
    return db.query(model).get(item_id)


def _get_project(db: Session, project_id: int) -> Project | None:
    if hasattr(db, "get"):
        return db.get(Project, project_id)
    return db.query(Project).get(project_id)


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    query = db.query(Note)
    if q:
        query = query.filter((Note.title.contains(q)) | (Note.content.contains(q)))
    if project_id is not None:
        query = query.filter(Note.project_id == project_id)

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        query = query.order_by(order_fn(getattr(Note, sort_field)))
    else:
        query = query.order_by(desc(Note.created_at))

    rows = query.offset(skip).limit(limit).all()
    return [to_read(NoteRead, row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    if payload.project_id is not None and not _get_project(db, payload.project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    note = Note(
        title=payload.title,
        content=payload.content,
        project_id=payload.project_id,
    )
    db.add(note)
    db.flush()
    db.refresh(note)
    return to_read(NoteRead, note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = _get_by_id(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    if payload.project_id is not None:
        if not _get_project(db, payload.project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        note.project_id = payload.project_id
    db.add(note)
    db.flush()
    db.refresh(note)
    return to_read(NoteRead, note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = _get_by_id(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return to_read(NoteRead, note)
