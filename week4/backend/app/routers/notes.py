from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note
from ..schemas import ActionItemRead, NoteCreate, NoteRead, NoteUpdate
from ..services.extract import extract_action_items

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    if not payload.title.strip() or not payload.content.strip():
        raise HTTPException(status_code=400, detail="Title and content are required")
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=list[NoteRead])
def search_notes(q: Optional[str] = None, db: Session = Depends(get_db)) -> list[NoteRead]:
    q = q.strip() if q else None
    if not q:
        rows = db.execute(select(Note)).scalars().all()
    else:
        q_lower = q.lower()
        rows = (
            db.execute(
                select(Note).where(
                    (func.lower(Note.title).contains(q_lower))
                    | (func.lower(Note.content).contains(q_lower))
                )
            )
            .scalars()
            .all()
        )
    return [NoteRead.model_validate(row) for row in rows]


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    if payload.title is None and payload.content is None:
        raise HTTPException(status_code=400, detail="Nothing to update")
    if payload.title is not None and not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if payload.content is not None and not payload.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()
    return Response(status_code=204)


@router.post("/{note_id}/extract", response_model=list[ActionItemRead])
def extract_note_action_items(note_id: int, db: Session = Depends(get_db)) -> list[ActionItemRead]:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    items = extract_action_items(note.content)
    created: list[ActionItem] = []
    for description in items:
        if not description.strip():
            continue
        created_item = ActionItem(description=description, completed=False)
        db.add(created_item)
        db.flush()
        db.refresh(created_item)
        created.append(created_item)
    return [ActionItemRead.model_validate(item) for item in created]
