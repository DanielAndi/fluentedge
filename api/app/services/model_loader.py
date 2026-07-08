"""Approved model loader (FR-ML-007, NFR-REL-002)."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.pipeline import Pipeline

from api.app.config import Settings, get_settings
from ml.models.registry import APPROVAL_TAG, APPROVED_VALUE, MODEL_NAME, configure_mlflow

logger = logging.getLogger(__name__)


@dataclass
class LoadedModel:
    pipeline: Pipeline
    version: str
    uri: str
    checksum: str | None = None


class ModelLoader:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._lock = threading.Lock()
        self._cached: LoadedModel | None = None

    def is_ready(self) -> bool:
        uri = self._settings.approved_model_uri.strip()
        version = self._settings.approved_model_version.strip()
        if uri.startswith("models:/") or uri.startswith("runs:/"):
            return bool(version or uri)
        return bool(uri and version)

    def load(self) -> LoadedModel:
        if not self.is_ready():
            raise RuntimeError("No approved model configured")
        with self._lock:
            if self._cached is not None:
                return self._cached
            configure_mlflow(self._settings.mlflow_tracking_uri)
            uri = self._settings.approved_model_uri.strip()
            version = self._settings.approved_model_version.strip()
            pipeline: Pipeline | None = None
            if uri.startswith("models:/"):
                self._verify_approval(version)
                try:
                    pipeline = mlflow.sklearn.load_model(uri)
                except OSError:
                    try:
                        pipeline = self._load_from_run_artifact(version)
                    except OSError:
                        pipeline = None
            elif uri.startswith("runs:/"):
                pipeline = mlflow.sklearn.load_model(uri)
            elif Path(uri).exists():
                from ml.models.predict import load_pipeline

                pipeline = load_pipeline(uri)
            else:
                pipeline = self._load_from_run_artifact(version)
            if pipeline is None:
                production = Path("/app/artifacts/production/model.joblib")
                if production.exists():
                    from ml.models.predict import load_pipeline

                    pipeline = load_pipeline(production)
            if pipeline is None or not isinstance(pipeline, Pipeline):
                raise RuntimeError("Loaded artifact is not a sklearn pipeline")
            self._cached = LoadedModel(
                pipeline=pipeline,
                version=version or uri,
                uri=uri,
            )
            logger.info("model_loaded version=%s", self._cached.version)
            return self._cached

    def _load_from_run_artifact(self, version: str) -> Pipeline:
        """Fallback when MLflow artifact files are missing from the shared volume."""
        client = MlflowClient()
        if version:
            mv = client.get_model_version(MODEL_NAME, version)
            run_id = mv.run_id
        else:
            versions = client.search_model_versions(f"name='{MODEL_NAME}'")
            run_id = max(versions, key=lambda v: int(v.version)).run_id
        local_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="model")
        return mlflow.sklearn.load_model(local_path)

    def clear_cache(self) -> None:
        with self._lock:
            self._cached = None

    def _verify_approval(self, version: str) -> None:
        if not version:
            return
        client = MlflowClient()
        mv = client.get_model_version(MODEL_NAME, version)
        if mv.tags.get(APPROVAL_TAG) != APPROVED_VALUE:
            raise RuntimeError(f"Model version {version} is not approved")


_loader: ModelLoader | None = None


def get_model_loader() -> ModelLoader:
    global _loader
    if _loader is None:
        _loader = ModelLoader()
    return _loader
