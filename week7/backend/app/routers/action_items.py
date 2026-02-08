from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Project
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead, to_read

router = APIRouter(prefix="/action-items", tags=["action_items"])


def _get_by_id(db: Session, model, item_id: int):
    if hasattr(db, "get"):
        return db.get(model, item_id)
    return db.query(model).get(item_id)


def _get_project(db: Session, project_id: int) -> Project | None:
    if hasattr(db, "get"):
        return db.get(Project, project_id)
    return db.query(Project).get(project_id)


@router.get("/", response_model=list[ActionItemRead])
def list_items(
    db: Session = Depends(get_db),
    completed: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at"),
) -> list[ActionItemRead]:
    query = db.query(ActionItem)
    if completed is not None:
        query = query.filter(ActionItem.completed.is_(completed))
    if project_id is not None:
        query = query.filter(ActionItem.project_id == project_id)

    sort_field = sort.lstrip("-")
    allowed_sort_fields = {"id", "description", "completed", "created_at", "updated_at"}
    if sort_field not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    order_fn = desc if sort.startswith("-") else asc
    query = query.order_by(order_fn(getattr(ActionItem, sort_field)))

    rows = query.offset(skip).limit(limit).all()
    return [to_read(ActionItemRead, row) for row in rows]


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    if payload.project_id is not None and not _get_project(db, payload.project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    item = ActionItem(
        description=payload.description,
        completed=False,
        project_id=payload.project_id,
    )
    db.add(item)
    db.flush()
    db.refresh(item)
    return to_read(ActionItemRead, item)


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = _get_by_id(db, ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return to_read(ActionItemRead, item)


@router.patch("/{item_id}", response_model=ActionItemRead)
def patch_item(item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)) -> ActionItemRead:
    item = _get_by_id(db, ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    if payload.description is None and payload.completed is None:
        raise HTTPException(status_code=400, detail="No fields provided")
    if payload.description is not None:
        item.description = payload.description
    if payload.completed is not None:
        item.completed = payload.completed
    if payload.project_id is not None:
        if not _get_project(db, payload.project_id):
            raise HTTPException(status_code=404, detail="Project not found")
        item.project_id = payload.project_id
    db.add(item)
    db.flush()
    db.refresh(item)
    return to_read(ActionItemRead, item)


@router.get("/{item_id}", response_model=ActionItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = _get_by_id(db, ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return to_read(ActionItemRead, item)


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    item = _get_by_id(db, ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    db.delete(item)
    db.flush()
    return Response(status_code=204)
