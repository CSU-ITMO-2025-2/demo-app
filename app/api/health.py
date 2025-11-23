import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def read_health():
    """
    Простой эндпоинт для liveness/readiness проб.
    """
    return {"status": "ok"}

@router.get("/message")
def read_message():
    """
    Возвращает текст из переменной окружения APP_MESSAGE
    или заглушку, если переменная не задана.
    """
    value = os.getenv("APP_MESSAGE")
    if not value:
        return {"message": "no APP_MESSAGE configured"}
    return {"message": value}