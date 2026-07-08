"""Prediction orchestration (FR-API-002, FR-API-003, NFR-PRIV-001)."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from api.app.config import Settings
from api.app.exceptions import APIError
from api.app.services.model_loader import LoadedModel, ModelLoader
from api.app.services.storage import StorageAdapter
from ml.data.schema import ClipRecord
from ml.features.audio import (
    AudioValidationError,
    encode_wav_bytes,
    load_audio_bytes,
    normalize_audio,
)
from ml.features.text import normalize_text
from ml.models.predict import predict_clip

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".wav", ".flac", ".mp3", ".m4a"}


def validate_upload(filename: str, data: bytes) -> None:
    suffix = Path(filename or "audio.wav").suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise APIError(
            "UNSUPPORTED_AUDIO_TYPE",
            "Upload a WAV, FLAC, MP3, or M4A file.",
            status_code=415,
        )
    try:
        load_audio_bytes(data, original_path=filename or "audio.wav")
    except AudioValidationError as exc:
        message = str(exc)
        if "10 MB" in message:
            raise APIError(
                "FILE_TOO_LARGE", "Upload a file smaller than 10 MB.", status_code=413
            ) from exc
        if "30 second" in message:
            raise APIError(
                "AUDIO_TOO_LONG", "Upload audio shorter than 30 seconds.", status_code=413
            ) from exc
        if "decode" in message.lower() or "Unsupported" in message:
            code = "UNSUPPORTED_AUDIO_TYPE" if "Unsupported" in message else "DECODE_FAILURE"
            raise APIError(code, message, status_code=400) from exc
        raise APIError(
            "DECODE_FAILURE", "Unable to decode the uploaded audio.", status_code=400
        ) from exc


def run_prediction(
    *,
    expected_phrase: str,
    filename: str,
    audio_bytes: bytes,
    request_id: str,
    settings: Settings,
    storage: StorageAdapter,
    loader: ModelLoader,
) -> dict:
    phrase = expected_phrase.strip()
    if not phrase:
        raise APIError("MISSING_PROMPT", "Provide an expected phrase to analyze.", status_code=400)

    validate_upload(filename, audio_bytes)

    if not loader.is_ready():
        raise APIError(
            "MODEL_NOT_READY",
            "No approved model is available for inference.",
            status_code=503,
        )

    object_key = ""
    try:
        object_key = storage.put_object(
            settings.s3_upload_bucket,
            audio_bytes,
            prefix="uploads",
            content_type="application/octet-stream",
            metadata={"request_id": request_id},
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "storage_upload_failed request_id=%s error=%s", request_id, type(exc).__name__
        )
        raise APIError(
            "DEPENDENCY_UNAVAILABLE",
            "Temporary storage is unavailable. Try again shortly.",
            status_code=503,
        ) from exc

    try:
        model = loader.load()
    except Exception as exc:  # noqa: BLE001
        logger.warning("model_load_failed request_id=%s error=%s", request_id, type(exc).__name__)
        raise APIError(
            "MODEL_NOT_READY",
            "Approved model could not be loaded.",
            status_code=503,
        ) from exc

    try:
        result = _predict_with_temp_file(
            model=model,
            expected_phrase=phrase,
            audio_bytes=audio_bytes,
            filename=filename,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("prediction_failed request_id=%s error=%s", request_id, type(exc).__name__)
        raise APIError(
            "PREDICTION_FAILURE",
            "Prediction could not be completed.",
            status_code=500,
        ) from exc
    finally:
        if object_key:
            try:
                storage.delete_object(settings.s3_upload_bucket, object_key)
            except Exception:  # noqa: BLE001
                logger.warning("upload_cleanup_failed request_id=%s", request_id)

    result["request_id"] = request_id
    result["model_version"] = f"fluentedge-baseline-{model.version}"
    return result


def _predict_with_temp_file(
    *,
    model: LoadedModel,
    expected_phrase: str,
    audio_bytes: bytes,
    filename: str,
) -> dict:
    waveform, sample_rate = load_audio_bytes(audio_bytes, original_path=filename or "audio.wav")
    waveform, sample_rate = normalize_audio(waveform, sample_rate)
    normalized_phrase = normalize_text(expected_phrase)

    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        audio_path = temp_dir / "attempt.wav"
        audio_path.write_bytes(encode_wav_bytes(waveform, sample_rate))
        clip = ClipRecord(
            clip_id="live_attempt",
            audio_uri=str(audio_path),
            transcript=expected_phrase,
            normalized_transcript=normalized_phrase,
            expected_phrase=normalized_phrase,
            source_release="live-upload",
        )
        return predict_clip(
            model.pipeline,
            clip,
            temp_dir,
            model_version=model.version,
        )
