"""Action items router with improved error handling and type safety."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from .. import db
from ..exceptions import DatabaseError, NotFoundError, ValidationError
from ..schemas import (
    ActionItemResponse,
    ExtractActionItemsRequest,
    ExtractActionItemsResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items_llm

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractActionItemsResponse)
def extract(request: ExtractActionItemsRequest) -> ExtractActionItemsResponse:
    """
    Extract action items from text using heuristic-based extraction.
    
    Args:
        request: Extraction request containing text and optional save_note flag
        
    Returns:
        Response containing extracted action items and optional note_id
    """
    try:
        note_id: Optional[int] = None
        if request.save_note:
            note_id = db.insert_note(request.text)

        items = extract_action_items_llm(request.text)
        action_items = db.insert_action_items(items, note_id=note_id)
        
        return ExtractActionItemsResponse(note_id=note_id, items=action_items)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: Optional[int] = Query(None, description="Filter by note ID")) -> list[ActionItemResponse]:
    """
    List all action items, optionally filtered by note_id.
    
    Args:
        note_id: Optional note ID to filter action items
        
    Returns:
        List of action items
    """
    try:
        return db.list_action_items(note_id=note_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, request: MarkDoneRequest) -> MarkDoneResponse:
    """
    Mark an action item as done or not done.
    
    Args:
        action_item_id: ID of the action item to update
        request: Request containing the done status
        
    Returns:
        Response with updated action item status
    """
    try:
        db.mark_action_item_done(action_item_id, request.done)
        return MarkDoneResponse(id=action_item_id, done=request.done)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}") from e


