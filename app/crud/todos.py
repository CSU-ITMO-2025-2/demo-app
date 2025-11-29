import logging

from db.models import TodoItem
from schemas.todos import TodoCreate
from sqlalchemy.orm import Session

from core.kafka_client import send_todo_created_event

logger = logging.getLogger(__name__)


def get_todos(db: Session):
    return db.query(TodoItem).all()


def get_todo_by_id(db: Session, todo_id: int):
    return db.query(TodoItem).filter(TodoItem.id == todo_id).first()


def create_todo(db: Session, todo: TodoCreate):
    db_todo = TodoItem(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    try:
        send_todo_created_event(todo_id=db_todo.id, title=db_todo.title)
    except Exception as e:
        logger.exception("Failed to emit todo_created event for %s: %s", db_todo.id, e)

    return db_todo


def update_todo(db: Session, db_todo: TodoItem, todo: TodoCreate):
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()

    try:
        send_todo_created_event(todo_id=db_todo.id, title=db_todo.title)
    except Exception as e:
        logger.exception("Failed to emit todo_updated event for %s: %s", db_todo.id, e)

    return db_todo


def delete_todo(db: Session, db_todo: TodoItem):
    db.delete(db_todo)
    db.commit()
    return db_todo
