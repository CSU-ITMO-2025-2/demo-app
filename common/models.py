from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from common.database import Base


class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)

    steps = relationship(
        "TodoStep",
        back_populates="todo",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TodoStep(Base):
    __tablename__ = "todo_steps"
    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id", ondelete="CASCADE"), index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)

    todo = relationship("TodoItem", back_populates="steps")
