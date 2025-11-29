from typing import List

from pydantic import BaseModel


class TodoStep(BaseModel):
    id: int
    todo_id: int
    description: str
    completed: bool

    class Config:
        orm_mode = True


class TodoCreate(BaseModel):
    title: str
    description: str
    completed: bool = False


class TodoItem(TodoCreate):
    id: int
    steps: List[TodoStep] = []

    class Config:
        orm_mode = True
