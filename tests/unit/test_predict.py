"""Prediction endpoint tests (FR-API-002, FR-API-004)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.services.model_loader import ModelLoader

FIXTURE_WAV = Path(__file__).resolve().parents[1] / "fixtures" / "synthetic" / "clip_000.wav"


@pytest.fixture
def client():
    return TestClient(app)


def test_predict_success(client, api_env, mock_model_loader):
    with FIXTURE_WAV.open("rb") as handle:
        response = client.post(
            "/predict",
            data={"expected_phrase": "the quick brown fox"},
            files={"file": ("clip_000.wav", handle, "audio/wav")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] in {"pass", "needs_review"}
    assert "confidence" in data
    assert "feedback_categories" in data
    assert data["model_version"].startswith("fluentedge-baseline-")
    assert "request_id" in data
    assert data["latency_ms"] >= 0


def test_predict_missing_prompt(client, api_env, mock_model_loader):
    with FIXTURE_WAV.open("rb") as handle:
        response = client.post(
            "/predict",
            data={"expected_phrase": "   "},
            files={"file": ("clip_000.wav", handle, "audio/wav")},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "MISSING_PROMPT"


def test_predict_unsupported_media(client, api_env, mock_model_loader):
    response = client.post(
        "/predict",
        data={"expected_phrase": "hello"},
        files={"file": ("bad.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415
    assert response.json()["error"]["code"] == "UNSUPPORTED_AUDIO_TYPE"


def test_predict_oversized_file(client, api_env, mock_model_loader):
    payload = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/predict",
        data={"expected_phrase": "hello"},
        files={"file": ("big.wav", payload, "audio/wav")},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_predict_decode_failure(client, api_env, mock_model_loader):
    response = client.post(
        "/predict",
        data={"expected_phrase": "hello"},
        files={"file": ("bad.wav", b"not-audio", "audio/wav")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "DECODE_FAILURE"


def test_predict_model_not_ready(client, api_env, monkeypatch):
    loader = ModelLoader()

    def not_ready(self):
        return False

    monkeypatch.setattr(ModelLoader, "is_ready", not_ready)
    monkeypatch.setattr("api.app.routers.predict.get_model_loader", lambda: loader)
    with FIXTURE_WAV.open("rb") as handle:
        response = client.post(
            "/predict",
            data={"expected_phrase": "hello"},
            files={"file": ("clip_000.wav", handle, "audio/wav")},
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MODEL_NOT_READY"


def test_ready_when_model_configured(client, api_env, mock_model_loader):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["model_ready"] is True


def test_health_contract(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "model_ready" in response.json()


def test_ui_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FluentEdge Speaking Feedback" in response.text


def test_performance_smoke(client, api_env, mock_model_loader):
    with FIXTURE_WAV.open("rb") as handle:
        response = client.post(
            "/predict",
            data={"expected_phrase": "the quick brown fox"},
            files={"file": ("clip_000.wav", handle, "audio/wav")},
        )
    assert response.status_code == 200
    assert response.json()["latency_ms"] < 2000
