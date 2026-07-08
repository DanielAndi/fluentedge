"""Application configuration (FR-INF-003, FR-INF-007, NFR-SEC-001)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FluentEdge"
    environment: str = "local"
    log_level: str = "INFO"

    # Storage (FR-INF-003)
    storage_backend: str = "s3"  # s3 | filesystem
    aws_region: str = "us-west-2"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    s3_endpoint_url: str = "http://localstack:4566"
    s3_upload_bucket: str = "fluentedge-uploads"
    s3_data_bucket: str = "fluentedge-data"
    s3_artifacts_bucket: str = "fluentedge-artifacts"
    filesystem_storage_root: str = "/data/local-storage"

    # Upload retention (NFR-PRIV-001)
    upload_retention_hours: int = 24

    # MLflow / model (FR-ML-007)
    mlflow_tracking_uri: str = "http://mlflow:5000"
    approved_model_uri: str = ""
    approved_model_version: str = ""

    # Service URLs for health checks
    prometheus_url: str = "http://prometheus:9090"
    grafana_url: str = "http://grafana:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
