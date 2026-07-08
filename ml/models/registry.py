"""MLflow model registry integration (FR-ML-002, FR-ML-006, FR-ML-007)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import mlflow
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.pipeline import Pipeline

MODEL_NAME = "fluentedge-baseline"
APPROVAL_TAG = "approval_status"
APPROVED_VALUE = "approved"
PENDING_VALUE = "pending_review"


def configure_mlflow(tracking_uri: str | None = None) -> None:
    uri = tracking_uri or os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(uri)


def register_model(
    pipeline: Pipeline,
    *,
    candidate_name: str,
    git_sha: str,
    manifest_hash: str,
    feature_schema_version: str,
    random_seed: int,
    metrics: dict[str, float],
    model_path: str | Path,
) -> str:
    """Register model in MLflow within the active run (approval remains pending)."""
    configure_mlflow()
    checksum = hashlib.sha256(Path(model_path).read_bytes()).hexdigest()
    mlflow.log_params(
        {
            "candidate_name": candidate_name,
            "git_sha": git_sha,
            "manifest_hash": manifest_hash,
            "feature_schema_version": feature_schema_version,
            "random_seed": random_seed,
            "artifact_checksum": checksum,
        }
    )
    for key, value in metrics.items():
        mlflow.log_metric(key, float(value))
    sample = [[0.0] * 9]
    signature = infer_signature(sample, pipeline.predict(sample))
    mlflow.sklearn.log_model(
        pipeline,
        artifact_path="model",
        registered_model_name=MODEL_NAME,
        signature=signature,
        input_example=sample,
    )
    mlflow.set_tag(APPROVAL_TAG, PENDING_VALUE)
    client = MlflowClient()
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    latest = max(versions, key=lambda v: int(v.version))
    client.set_model_version_tag(latest.name, latest.version, APPROVAL_TAG, PENDING_VALUE)
    return latest.version


def approve_model(version: str, *, approver: str = "project-owner") -> None:
    """Explicit human approval step (FR-ML-006); never automatic."""
    configure_mlflow()
    client = MlflowClient()
    client.transition_model_version_stage(
        name=MODEL_NAME,
        version=version,
        stage="Production",
        archive_existing_versions=True,
    )
    client.set_model_version_tag(MODEL_NAME, version, APPROVAL_TAG, APPROVED_VALUE)
    client.set_model_version_tag(MODEL_NAME, version, "approved_by", approver)


def get_production_model_uri() -> tuple[str, str]:
    configure_mlflow()
    client = MlflowClient()
    versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
    if not versions:
        return "", ""
    version = versions[0]
    approval = version.tags.get(APPROVAL_TAG, PENDING_VALUE)
    if approval != APPROVED_VALUE:
        return "", ""
    return version.source, version.version
