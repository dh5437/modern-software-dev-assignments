from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class NotePatch(BaseModel):
    title: str | None = None
    content: str | None = None


class ActionItemCreate(BaseModel):
    description: str


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class ActionItemPatch(BaseModel):
    description: str | None = None
    completed: bool | None = None


def model_to_read(schema_cls: type[BaseModel], obj: object) -> BaseModel:
    if hasattr(schema_cls, "model_validate"):
        return schema_cls.model_validate(obj)
    return schema_cls.from_orm(obj)

