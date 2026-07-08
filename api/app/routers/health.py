"""Health endpoint (FR-API-001, FR-INF-008)."""

import time
import uuid

from fastapi import APIRouter, Request

from api.app.config import get_settings
from api.app.metrics import REQUEST_COUNT, REQUEST_LATENCY
from api.app.schemas import DependencyStatus, HealthResponse
from api.app.services.health import (
    aggregate_status,
    check_mlflow,
    check_model,
    check_storage,
    get_storage,
)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    settings = get_settings()
    storage = get_storage(settings)

    start = time.perf_counter()
    deps_raw = {
        "storage": check_storage(storage, settings.s3_upload_bucket),
        "mlflow": check_mlflow(settings),
        "model": check_model(settings),
    }
    deps = {name: DependencyStatus(**value) for name, value in deps_raw.items()}
    model_ready = deps_raw["model"].get("status") == "ready"
    status = aggregate_status(deps_raw)
    if status == "ok" and not model_ready:
        status = "ok"  # API is healthy even without model

    elapsed = time.perf_counter() - start
    REQUEST_LATENCY.labels(method="GET", endpoint="/health").observe(elapsed)
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()

    return HealthResponse(
        status=status,
        request_id=request_id,
        dependencies=deps,
        model_ready=model_ready,
    )
