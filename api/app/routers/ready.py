"""Readiness endpoint (FR-API-001)."""

import uuid

from fastapi import APIRouter, Request, Response

from api.app.config import get_settings
from api.app.metrics import ACTIVE_MODEL_VERSION, MODEL_READY
from api.app.schemas import ReadyResponse
from api.app.services.health import check_storage, get_storage
from api.app.services.model_loader import get_model_loader

router = APIRouter(tags=["health"])


@router.get("/ready", response_model=ReadyResponse)
async def ready(request: Request, response: Response) -> ReadyResponse:
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    settings = get_settings()
    loader = get_model_loader()
    storage = get_storage(settings)

    storage_ok = check_storage(storage, settings.s3_upload_bucket).get("status") == "ok"
    model_ready = loader.is_ready() and storage_ok
    version = settings.approved_model_version if model_ready else None

    MODEL_READY.set(1 if model_ready else 0)
    if version:
        ACTIVE_MODEL_VERSION.labels(version=version).set(1)

    if not model_ready:
        response.status_code = 503

    return ReadyResponse(
        status="ready" if model_ready else "not_ready",
        request_id=request_id,
        model_ready=model_ready,
        model_version=version,
    )
