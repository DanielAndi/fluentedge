"""Prediction endpoint (FR-API-002, FR-API-003, FR-API-005)."""

import logging
import time
import uuid

from fastapi import APIRouter, File, Form, Request, UploadFile

from api.app.config import get_settings
from api.app.metrics import CONFIDENCE_SUMMARY, MODEL_READY, PREDICTION_COUNT, ACTIVE_MODEL_VERSION
from api.app.schemas import PredictResponse
from api.app.services.health import get_storage
from api.app.services.inference import run_prediction
from api.app.services.model_loader import get_model_loader

router = APIRouter(tags=["predict"])
logger = logging.getLogger(__name__)


@router.post("/predict", response_model=PredictResponse)
async def predict(
    request: Request,
    expected_phrase: str = Form(...),
    file: UploadFile = File(...),
) -> PredictResponse:
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
    settings = get_settings()
    storage = get_storage(settings)
    loader = get_model_loader()

    start = time.perf_counter()
    audio_bytes = await file.read()
    # FR-API-005: log request metadata only, never raw audio or full transcript
    logger.info(
        "predict_start request_id=%s bytes=%s media_type=%s",
        request_id,
        len(audio_bytes),
        file.content_type or "unknown",
    )

    result = run_prediction(
        expected_phrase=expected_phrase,
        filename=file.filename or "audio.wav",
        audio_bytes=audio_bytes,
        request_id=request_id,
        settings=settings,
        storage=storage,
        loader=loader,
    )

    total_ms = int((time.perf_counter() - start) * 1000)
    latency_ms = max(result.get("latency_ms", 0), total_ms)

    PREDICTION_COUNT.labels(label=result["label"]).inc()
    CONFIDENCE_SUMMARY.observe(result["confidence"])
    MODEL_READY.set(1)
    ACTIVE_MODEL_VERSION.labels(version=result["model_version"]).set(1)

    logger.info(
        "predict_complete request_id=%s label=%s latency_ms=%s",
        request_id,
        result["label"],
        latency_ms,
    )

    return PredictResponse(
        request_id=request_id,
        score=result["score"],
        label=result["label"],
        confidence=result["confidence"],
        feedback_categories=result["feedback_categories"],
        model_version=result["model_version"],
        latency_ms=latency_ms,
    )
