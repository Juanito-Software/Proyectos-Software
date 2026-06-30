from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db


router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_or_create_tags(names: list[str], db: Session) -> list[models.Tag]:
    tags = []
    for name in names:
        tag = db.query(models.Tag).filter(models.Tag.name == name.lower()).first()
        if not tag:
            tag = models.Tag(name=name.lower())
            db.add(tag)
        tags.append(tag)
    return tags


@router.get("/", response_model=list[schemas.TaskPublic])
def list_tasks(
    completed: bool | None = Query(default=None),
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Task).filter(models.Task.owner_id == current_user.id)

    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if tag:
        query = query.join(models.Task.tags).filter(models.Tag.name == tag.lower())

    return query.all()


@router.post("/", response_model=schemas.TaskPublic, status_code=201)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        owner_id=current_user.id,
        tags=_get_or_create_tags(task_in.tag_names, db),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=schemas.TaskPublic)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskPublic)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    update_data = task_in.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tag_names", None)

    for field, value in update_data.items():
        setattr(task, field, value)

    if tag_names is not None:
        task.tags = _get_or_create_tags(tag_names, db)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == current_user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(task)
    db.commit()
