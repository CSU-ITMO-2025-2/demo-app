from typing import List

from crud import todos as crud_todos
from db.database import get_db
from fastapi import APIRouter, Depends, HTTPException
from schemas.todos import TodoCreate, TodoItem
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/todos", response_model=List[TodoItem])
def read_todos(db: Session = Depends(get_db)):
    1 / 0
    return crud_todos.get_todos(db)


@router.get("/todos/{todo_id}", response_model=TodoItem)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = crud_todos.get_todo_by_id(db, todo_id)

    if todo is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return todo


@router.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    return crud_todos.create_todo(db, todo)


@router.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = crud_todos.get_todo_by_id(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud_todos.update_todo(db, db_todo, todo)


@router.delete("/todos/{todo_id}", response_model=TodoItem)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud_todos.get_todo_by_id(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud_todos.delete_todo(db, db_todo)
