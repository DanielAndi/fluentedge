"""Markdown model card generation (FR-ML-005, §7.3)."""

from __future__ import annotations

from datetime import UTC, datetime

from ml.evaluation.evaluate import CandidateEvaluation


def render_model_card(
    *,
    candidate: CandidateEvaluation,
    git_sha: str,
    manifest_hash: str,
    feature_schema_version: str,
    random_seed: int,
    artifact_checksum: str,
    dataset_note: str,
) -> str:
    now = datetime.now(UTC).isoformat()
    metrics = candidate.metrics
    confusion = candidate.confusion
    return f"""# FluentEdge Model Card

**Generated:** {now}  
**Candidate:** {candidate.name}  
**Git SHA:** {git_sha}  
**Manifest hash:** {manifest_hash}  
**Feature schema:** {feature_schema_version}  
**Random seed:** {random_seed}  
**Artifact checksum:** {artifact_checksum}

## Intended use

Prototype phrase-similarity feedback for controlled English prompts. This is **not** clinical pronunciation grading.

## Dataset note

{dataset_note}

## Metrics

| Metric | Value |
|--------|-------|
| Macro F1 | {metrics["macro_f1"]:.4f} |
| Precision (pass) | {metrics["precision_pass"]:.4f} |
| Recall (pass) | {metrics["recall_pass"]:.4f} |
| Precision (needs_review) | {metrics["precision_needs_review"]:.4f} |
| Recall (needs_review) | {metrics["recall_needs_review"]:.4f} |
| WER mean | {metrics["wer_mean"]:.4f} |
| CER mean | {metrics["cer_mean"]:.4f} |
| Latency p95 (ms) | {metrics["latency_p95_ms"]:.2f} |
| Quality gate | {"pass" if candidate.gate_passed else "fail"} |

## Confusion matrix

| | Pred 0 | Pred 1 |
|--|--------|--------|
| True 0 | {confusion["tn"]} | {confusion["fp"]} |
| True 1 | {confusion["fn"]} | {confusion["tp"]} |

## Confidence limitations

Probabilities come from the sklearn classifier and are not formally calibrated. Treat confidence as a ranking aid only.

## Approval

Models require explicit `make approve-model` before production use (FR-ML-006).
"""
