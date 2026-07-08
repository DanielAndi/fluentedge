"""Evaluation metrics (FR-ML-004, FR-ML-005, FR-DI-007)."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

MACRO_F1_THRESHOLD = 0.75


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_pass": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "recall_pass": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "precision_needs_review": float(precision_score(y_true, y_pred, pos_label=0, zero_division=0)),
        "recall_needs_review": float(recall_score(y_true, y_pred, pos_label=0, zero_division=0)),
    }


def confusion_matrix_dict(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, int]:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    return {
        "tn": int(matrix[0, 0]),
        "fp": int(matrix[0, 1]),
        "fn": int(matrix[1, 0]),
        "tp": int(matrix[1, 1]),
    }


def speech_error_summaries(frame: pd.DataFrame) -> dict[str, float]:
    return {
        "wer_mean": float(frame["wer"].mean()),
        "wer_median": float(frame["wer"].median()),
        "wer_p95": float(frame["wer"].quantile(0.95)),
        "cer_mean": float(frame["cer"].mean()),
        "cer_median": float(frame["cer"].median()),
        "cer_p95": float(frame["cer"].quantile(0.95)),
    }


def measure_inference_latency(predict_fn, samples: np.ndarray, *, warmup: int = 3) -> dict[str, float]:
    for idx in range(min(warmup, len(samples))):
        predict_fn(samples[idx : idx + 1])
    latencies: list[float] = []
    for row in samples:
        start = time.perf_counter()
        predict_fn(row.reshape(1, -1))
        latencies.append(time.perf_counter() - start)
    series = np.array(latencies)
    return {
        "latency_p50_ms": float(np.percentile(series, 50) * 1000),
        "latency_p95_ms": float(np.percentile(series, 95) * 1000),
    }


def gate_passed(macro_f1: float) -> bool:
    return macro_f1 >= MACRO_F1_THRESHOLD
