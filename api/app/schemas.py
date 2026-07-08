"""Pydantic schemas for API responses (FR-API-001, FR-API-003)."""

from typing import Literal

from pydantic import BaseModel, Field


class DependencyStatus(BaseModel):
    status: str
    message: str | None = None
    bucket: str | None = None
    version: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded", "unavailable"]
    service: str = "fluentedge-api"
    request_id: str
    dependencies: dict[str, DependencyStatus]
    model_ready: bool = Field(description="True when an approved model is available")


class ReadyResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    service: str = "fluentedge-api"
    request_id: str
    model_ready: bool
    model_version: str | None = None


class PredictResponse(BaseModel):
    request_id: str
    score: float
    label: Literal["pass", "needs_review"]
    confidence: float
    feedback_categories: list[str]
    model_version: str
    latency_ms: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    request_id: str
    error: ErrorDetail
