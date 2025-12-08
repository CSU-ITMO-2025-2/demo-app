import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def read_health():
    """
    Простой эндпоинт для liveness/readiness проб.
    """
    return {"status": "okay"}

@router.get("/burn")
def burn():
    x = 0
    for i in range(50_000_000):
        x += i
    return {"result": x}
