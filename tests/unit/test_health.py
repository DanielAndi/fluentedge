"""Health endpoint tests (FR-API-001, FR-INF-008)."""

from fastapi.testclient import TestClient

from api.app.main import app

client = TestClient(app)


def test_health_returns_schema():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "request_id" in data
    assert "dependencies" in data
    assert "model_ready" in data
    assert data["dependencies"]["model"]["status"] in {"ready", "not_ready"}


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "fluentedge_requests_total" in response.text


def test_request_id_header():
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
