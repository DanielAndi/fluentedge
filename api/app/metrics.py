"""Prometheus metrics (FR-API-006, NFR-OBS-001, NFR-OBS-002)."""

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter(
    "fluentedge_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "fluentedge_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)
ERROR_COUNT = Counter(
    "fluentedge_errors_total",
    "API errors by code",
    ["code"],
)
PREDICTION_COUNT = Counter(
    "fluentedge_predictions_total",
    "Total predictions by label",
    ["label"],
)
CONFIDENCE_SUMMARY = Histogram(
    "fluentedge_prediction_confidence",
    "Prediction confidence distribution",
    buckets=(0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1.0),
)
ACTIVE_MODEL_VERSION = Gauge(
    "fluentedge_active_model_version_info",
    "Active model version indicator",
    ["version"],
)
MODEL_READY = Gauge(
    "fluentedge_model_ready",
    "Whether an approved model is loaded and ready (1=yes)",
)
DEPENDENCY_HEALTH = Gauge(
    "fluentedge_dependency_up",
    "Dependency health (1=up, 0=down)",
    ["dependency"],
)
