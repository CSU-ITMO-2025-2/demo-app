import os

from fastapi import APIRouter, Response
from prometheus_client import (
    CollectorRegistry,
    CONTENT_TYPE_LATEST,
    REGISTRY,
    generate_latest,
    multiprocess,
)

router = APIRouter()


@router.get("/metrics")
def metrics() -> Response:
    """
    Expose Prometheus metrics for the FastAPI process.
    Supports multiprocess mode when PROMETHEUS_MULTIPROC_DIR is set.
    """
    registry = REGISTRY

    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
