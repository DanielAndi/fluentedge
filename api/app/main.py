"""FluentEdge API application (FR-API-001, NFR-OBS-002)."""

import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from api.app.config import get_settings
from api.app.exceptions import APIError, api_error_handler
from api.app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from api.app.routers.health import router as health_router
from api.app.routers.predict import router as predict_router
from api.app.routers.ready import router as ready_router

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"

app = FastAPI(
    title="FluentEdge API",
    description="Local-first speaking feedback API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(APIError, api_error_handler)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RedactingFilter(logging.Filter):
    """Block accidental logging of sensitive payloads (NFR-PRIV-002)."""

    SENSITIVE_MARKERS = ("raw_audio", "access_token", "bearer ", "authorization:")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage().lower()
        return not any(marker in message for marker in self.SENSITIVE_MARKERS)


logging.getLogger("api").addFilter(RedactingFilter())


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    endpoint = request.url.path
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(elapsed)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api")
async def api_info():
    settings = get_settings()
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "predict": "/predict",
        "metrics": "/metrics",
    }


@app.get("/")
async def learner_ui():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return await api_info()


app.include_router(health_router)
app.include_router(ready_router)
app.include_router(predict_router)
