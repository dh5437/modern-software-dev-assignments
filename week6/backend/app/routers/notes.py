from pathlib import Path
import shlex
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, text
from sqlalchemy.orm import Session

from ..db import get_db, session_get
from ..models import Note
from ..schemas import NoteCreate, NotePatch, NoteRead, model_to_read

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(50, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteRead]:
    query = db.query(Note)
    if q:
        query = query.filter((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        query = query.order_by(order_fn(getattr(Note, sort_field)))
    else:
        query = query.order_by(desc(Note.created_at))

    rows = query.offset(skip).limit(limit).all()
    return [model_to_read(NoteRead, row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return model_to_read(NoteRead, note)


@router.patch("/{note_id}", response_model=NoteRead)
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:
    note = session_get(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return model_to_read(NoteRead, note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = session_get(db, Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return model_to_read(NoteRead, note)


@router.get("/unsafe-search", response_model=list[NoteRead])
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:
    query = db.query(Note)
    if q:
        query = query.filter((Note.title.contains(q)) | (Note.content.contains(q)))
    rows = query.order_by(desc(Note.created_at)).limit(50).all()
    return [model_to_read(NoteRead, row) for row in rows]


@router.get("/debug/hash-md5")
def debug_hash_md5(q: str) -> dict[str, str]:
    import hashlib

    return {"algo": "md5", "hex": hashlib.md5(q.encode()).hexdigest()}


@router.get("/debug/eval")
def debug_eval(expr: str) -> dict[str, str]:
    import ast

    try:
        result = ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        raise HTTPException(status_code=400, detail="Invalid expression")
    return {"result": result}


@router.get("/debug/run")
def debug_run(cmd: str) -> dict[str, str]:
    import subprocess

    parts = shlex.split(cmd)
    if not parts:
        raise HTTPException(status_code=400, detail="Command required")
    allowed = {"echo"}
    if parts[0] not in allowed:
        raise HTTPException(status_code=400, detail="Command not allowed")
    completed = subprocess.run(parts, shell=False, capture_output=True, text=True)
    return {"returncode": str(completed.returncode), "stdout": completed.stdout, "stderr": completed.stderr}


@router.get("/debug/fetch")
def debug_fetch(url: str) -> dict[str, str]:
    from urllib.request import urlopen

    with urlopen(url) as res:  # noqa: S310
        body = res.read(1024).decode(errors="ignore")
    return {"snippet": body}


@router.get("/debug/read")
def debug_read(path: str) -> dict[str, str]:
    try:
        base_dir = Path("data").resolve()
        candidate = (base_dir / path).resolve()
        if not str(candidate).startswith(str(base_dir) + "/"):
            raise HTTPException(status_code=400, detail="Invalid path")
        content = candidate.read_text()[:1024]
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
    return {"snippet": content}
