"""Baseline model training (FR-ML-001, FR-ML-003)."""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class TrainedCandidate:
    name: str
    pipeline: Pipeline
    train_accuracy: float


def build_candidates(random_seed: int = 42) -> dict[str, Pipeline]:
    return {
        "logistic_regression": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000, random_state=random_seed, class_weight="balanced"
                    ),
                ),
            ]
        ),
        "random_forest": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=100,
                        random_state=random_seed,
                        class_weight="balanced",
                    ),
                ),
            ]
        ),
    }


def train_candidates(
    x_train: np.ndarray,
    y_train: np.ndarray,
    *,
    random_seed: int = 42,
) -> list[TrainedCandidate]:
    results: list[TrainedCandidate] = []
    for name, pipeline in build_candidates(random_seed).items():
        pipeline.fit(x_train, y_train)
        preds = pipeline.predict(x_train)
        acc = float(np.mean(preds == y_train))
        results.append(TrainedCandidate(name=name, pipeline=pipeline, train_accuracy=acc))
    return results


def save_model(pipeline: Pipeline, path: str) -> None:
    joblib.dump(pipeline, path)


def load_model(path: str) -> Pipeline:
    return joblib.load(path)
