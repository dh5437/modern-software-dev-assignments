from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NotePatch, NoteRead, to_read

router = APIRouter(prefix="/notes", tags=["notes"])


def _get_by_id(db: Session, model, item_id: int):
    if hasattr(db, "get"):
        return db.get(model, item_id)
    return db.query(model).get(item_id)


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    query = db.query(Note)
    if q:
        query = query.filter((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    allowed_sort_fields = {"id", "title", "content", "created_at", "updated_at"}
    if sort_field not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    order_fn = desc if sort.startswith("-") else asc
    query = query.order_by(order_fn(getattr(Note, sort_field)))

    rows = query.offset(skip).limit(limit).all()
    return [to_read(NoteRead, row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return to_read(NoteRead, note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = _get_by_id(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is None and payload.content is None:
        raise HTTPException(status_code=400, detail="No fields provided")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
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


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = _get_by_id(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()
    return Response(status_code=204)
