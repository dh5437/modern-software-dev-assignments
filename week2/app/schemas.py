"""Pydantic schemas for API request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Note Schemas
class NoteBase(BaseModel):
    """Base schema for note data."""
    content: str = Field(..., min_length=1, description="Note content")


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass


class NoteResponse(NoteBase):
    """Schema for note response."""
    id: int = Field(..., description="Note ID")
    created_at: str = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Action Item Schemas
class ActionItemBase(BaseModel):
    """Base schema for action item data."""
    text: str = Field(..., min_length=1, description="Action item text")
    note_id: Optional[int] = Field(None, description="Associated note ID")


class ActionItemCreate(ActionItemBase):
    """Schema for creating a new action item."""
    pass


class ActionItemResponse(ActionItemBase):
    """Schema for action item response."""
    id: int = Field(..., description="Action item ID")
    done: bool = Field(default=False, description="Completion status")
    created_at: str = Field(default="", description="Creation timestamp")

    class Config:
        from_attributes = True


# Request Schemas
class ExtractActionItemsRequest(BaseModel):
    """Schema for action item extraction request."""
    text: str = Field(..., min_length=1, description="Text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the note")


class ExtractActionItemsResponse(BaseModel):
    """Schema for action item extraction response."""
    note_id: Optional[int] = Field(None, description="Saved note ID if save_note was True")
    items: list[ActionItemResponse] = Field(..., description="Extracted action items")


class MarkDoneRequest(BaseModel):
    """Schema for marking action item as done."""
    done: bool = Field(default=True, description="Completion status")


class MarkDoneResponse(BaseModel):
    """Schema for mark done response."""
    id: int = Field(..., description="Action item ID")
    done: bool = Field(..., description="Completion status")

