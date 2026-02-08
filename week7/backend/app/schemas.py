from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str
    content: str
    project_id: int | None = None


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None
    project_id: int | None = None


class ActionItemCreate(BaseModel):
    description: str
    project_id: int | None = None


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    project_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


def to_read(model, obj):
    if hasattr(model, "model_validate"):
        return model.model_validate(obj)
    return model.from_orm(obj)


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None
    project_id: int | None = None


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        orm_mode = True


class ProjectPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = None
