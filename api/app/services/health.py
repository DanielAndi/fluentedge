"""Dependency and model health probes."""

from __future__ import annotations

import os
from pathlib import Path

import httpx

from api.app.config import Settings
from api.app.metrics import DEPENDENCY_HEALTH
from api.app.services.storage import StorageAdapter, create_storage_adapter


def get_storage(settings: Settings) -> StorageAdapter:
    return create_storage_adapter(
        settings.storage_backend,
        endpoint_url=settings.s3_endpoint_url,
        region=settings.aws_region,
        access_key_id=settings.aws_access_key_id,
        secret_access_key=settings.aws_secret_access_key,
        filesystem_root=settings.filesystem_storage_root,
    )


def check_storage(storage: StorageAdapter, bucket: str) -> dict:
    try:
        ok = storage.bucket_exists(bucket)
        DEPENDENCY_HEALTH.labels(dependency="storage").set(1 if ok else 0)
        return {"status": "ok" if ok else "unavailable", "bucket": bucket}
    except Exception as exc:  # noqa: BLE001 - health must not crash
        DEPENDENCY_HEALTH.labels(dependency="storage").set(0)
        return {"status": "unavailable", "message": type(exc).__name__}


def check_mlflow(settings: Settings) -> dict:
    try:
        response = httpx.get(f"{settings.mlflow_tracking_uri}/health", timeout=3.0)
        ok = response.status_code == 200
        DEPENDENCY_HEALTH.labels(dependency="mlflow").set(1 if ok else 0)
        return {"status": "ok" if ok else "unavailable"}
    except Exception as exc:  # noqa: BLE001
        DEPENDENCY_HEALTH.labels(dependency="mlflow").set(0)
        return {"status": "unavailable", "message": type(exc).__name__}


def check_model(settings: Settings) -> dict:
    """Distinguish service health from model readiness (FR-INF-008)."""
    uri = settings.approved_model_uri.strip()
    version = settings.approved_model_version.strip()
    if not uri and not version:
        DEPENDENCY_HEALTH.labels(dependency="model").set(0)
        return {
            "status": "not_ready",
            "message": "No approved model configured; inference unavailable",
        }
    if uri and Path(uri).exists():
        DEPENDENCY_HEALTH.labels(dependency="model").set(1)
        return {"status": "ready", "version": version or "local-artifact"}
    if uri.startswith("models:/") or uri.startswith("runs:/"):
        DEPENDENCY_HEALTH.labels(dependency="model").set(1)
        return {"status": "ready", "version": version or uri}
    DEPENDENCY_HEALTH.labels(dependency="model").set(0)
    return {
        "status": "not_ready",
        "message": "Approved model URI not found on disk or registry",
    }


def aggregate_status(dependencies: dict[str, dict]) -> str:
    """Return ok when core services are up; degraded when model is not ready."""
    storage = dependencies.get("storage", {}).get("status")
    mlflow = dependencies.get("mlflow", {}).get("status")
    if storage != "ok" or mlflow != "ok":
        return "degraded"
    return "ok"
