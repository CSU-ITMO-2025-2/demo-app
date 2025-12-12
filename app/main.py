from api import todos, health, metrics
from db import database, models
from fastapi import FastAPI, Request
from prometheus_client import Counter

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests processed by the FastAPI service",
    ["method", "path", "status"],
)

@app.middleware("http")
async def count_http_requests(request: Request, call_next):
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)
        http_requests_total.labels(
            method=request.method,
            path=path_template,
            status=str(status_code),
        ).inc()

app.include_router(todos.router)
app.include_router(health.router)
app.include_router(metrics.router)
