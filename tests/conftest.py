"""Shared API test fixtures."""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from api.app.config import get_settings
from api.app.services.model_loader import LoadedModel, ModelLoader


@pytest.fixture
def trained_pipeline() -> Pipeline:
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=200)),
        ]
    )
    rng = np.random.default_rng(42)
    x = rng.normal(size=(20, 9))
    y = np.array([1] * 10 + [0] * 10)
    pipeline.fit(x, y)
    return pipeline


@pytest.fixture
def mock_model_loader(monkeypatch, trained_pipeline):
    loader = ModelLoader()
    loader._cached = LoadedModel(  # noqa: SLF001
        pipeline=trained_pipeline,
        version="test-1",
        uri="models:/fluentedge-baseline/test-1",
    )

    def fake_get_loader():
        return loader

    monkeypatch.setattr("api.app.services.model_loader.get_model_loader", fake_get_loader)
    monkeypatch.setattr("api.app.routers.predict.get_model_loader", fake_get_loader)
    monkeypatch.setattr("api.app.routers.ready.get_model_loader", fake_get_loader)
    return loader


@pytest.fixture
def api_env(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_BACKEND", "filesystem")
    monkeypatch.setenv("FILESYSTEM_STORAGE_ROOT", str(tmp_path / "storage"))
    monkeypatch.setenv("APPROVED_MODEL_URI", "models:/fluentedge-baseline/1")
    monkeypatch.setenv("APPROVED_MODEL_VERSION", "1")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
