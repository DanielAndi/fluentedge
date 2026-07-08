"""Candidate evaluation and comparison (FR-ML-003, FR-ML-004, FR-ML-005)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.evaluation.metrics import (
    classification_metrics,
    confusion_matrix_dict,
    gate_passed,
    measure_inference_latency,
    speech_error_summaries,
)
from ml.models.train import TrainedCandidate


@dataclass
class CandidateEvaluation:
    name: str
    metrics: dict[str, float]
    confusion: dict[str, int]
    gate_passed: bool


def evaluate_candidate(
    candidate: TrainedCandidate,
    x_test: np.ndarray,
    y_test: np.ndarray,
    feature_frame: pd.DataFrame,
) -> CandidateEvaluation:
    preds = candidate.pipeline.predict(x_test)
    metrics = classification_metrics(y_test, preds)
    metrics.update(speech_error_summaries(feature_frame))
    metrics.update(
        measure_inference_latency(
            lambda batch: candidate.pipeline.predict(batch),
            x_test,
        )
    )
    return CandidateEvaluation(
        name=candidate.name,
        metrics=metrics,
        confusion=confusion_matrix_dict(y_test, preds),
        gate_passed=gate_passed(metrics["macro_f1"]),
    )


def compare_candidates(evaluations: list[CandidateEvaluation]) -> dict:
    ranked = sorted(evaluations, key=lambda item: item.metrics["macro_f1"], reverse=True)
    return {
        "winner": ranked[0].name if ranked else None,
        "comparison": [
            {
                "name": item.name,
                "macro_f1": item.metrics["macro_f1"],
                "gate_passed": item.gate_passed,
                "latency_p95_ms": item.metrics["latency_p95_ms"],
            }
            for item in ranked
        ],
    }


def select_winner(evaluations: list[CandidateEvaluation]) -> CandidateEvaluation | None:
    passing = [item for item in evaluations if item.gate_passed]
    if not passing:
        return None
    return sorted(passing, key=lambda item: item.metrics["macro_f1"], reverse=True)[0]
