"""Inference helpers (FR-ML-007, FR-ML-008)."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.pipeline import Pipeline

from ml.data.schema import ClipRecord, LabelName
from ml.features.build import FEATURE_COLUMNS, extract_clip_features


def artifact_checksum(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return hashlib.sha256(data).hexdigest()


def predict_clip(
    pipeline: Pipeline,
    clip: ClipRecord,
    base_dir: Path,
    *,
    model_version: str,
) -> dict:
    start = time.perf_counter()
    features = extract_clip_features(clip, base_dir)
    vector = np.array([[features[col] for col in FEATURE_COLUMNS]], dtype=float)
    proba = None
    if hasattr(pipeline, "predict_proba"):
        proba = float(pipeline.predict_proba(vector)[0][1])
    pred = int(pipeline.predict(vector)[0])
    label = LabelName.PASS if pred == 1 else LabelName.NEEDS_REVIEW
    confidence = proba if proba is not None else (0.9 if label == LabelName.PASS else 0.6)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return {
        "label": label.value,
        "confidence": round(confidence, 4),
        "score": round(confidence * 100, 1),
        "model_version": model_version,
        "latency_ms": latency_ms,
        "feedback_categories": _feedback_categories(features),
    }


def load_pipeline(path: str | Path) -> Pipeline:
    return joblib.load(path)


def _feedback_categories(features: dict[str, float]) -> list[str]:
    categories: list[str] = []
    if features["wer"] > 0.2:
        categories.append("word_difference")
    if features["cer"] > 0.15:
        categories.append("character_difference")
    if features["silence_ratio"] > 0.4:
        categories.append("high_silence_ratio")
    if not categories:
        categories.append("minor_word_timing_difference")
    return categories
