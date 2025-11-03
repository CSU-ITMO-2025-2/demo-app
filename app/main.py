from api import todos, health
from db import database, models
from fastapi import FastAPI

# Инициализация базы данных
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Подключение маршрутов
app.include_router(todos.router)
app.include_router(health.router)
