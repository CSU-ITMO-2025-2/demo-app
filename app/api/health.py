import os
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def read_health():
    """
    Простой эндпоинт для liveness/readiness проб.
    """
    return {"status": "okay"}
