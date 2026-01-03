"""Notes router with improved error handling and type safety."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..exceptions import DatabaseError, NotFoundError, ValidationError
from ..schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(request: NoteCreate) -> NoteResponse:
    """
    Create a new note.
    
    Args:
        request: Note creation request containing content
        
    Returns:
        Created note response
    """
    try:
        note_id = db.insert_note(request.content)
        return db.get_note(note_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Get a single note by ID.
    
    Args:
        note_id: ID of the note to retrieve
        
    Returns:
        Note response
    """
    try:
        return db.get_note(note_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[NoteResponse]:
    """
    List all notes.
    
    Returns:
        List of all notes
    """
    try:
        return db.list_notes()
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


