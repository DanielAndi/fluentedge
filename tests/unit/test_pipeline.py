"""Pipeline and registry tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ml.evaluation.evaluate import evaluate_candidate, select_winner
from ml.evaluation.metrics import gate_passed
from ml.features.build import build_feature_frame, feature_matrix
from ml.models.predict import artifact_checksum, load_pipeline
from ml.models.train import train_candidates
from ml.pipeline.local_pipeline import run_pipeline


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "synthetic"


def test_quality_gate_threshold():
    assert gate_passed(0.75) is True
    assert gate_passed(0.74) is False


def test_train_and_evaluate_candidates(fixture_dir: Path):
    from ml.data.preprocess import preprocess_clip
    from ml.data.schema import Manifest
    from ml.data.split import assign_splits

    manifest = Manifest.model_validate_json((fixture_dir / "manifest.json").read_text())
    processed = [preprocess_clip(clip, fixture_dir) for clip in manifest.clips]
    assigned = assign_splits(processed, seed=42)
    frame = build_feature_frame(assigned, fixture_dir)
    train_df = frame[frame["split"] == "train"]
    test_df = frame[frame["split"] == "test"]
    x_train, y_train = feature_matrix(train_df)
    x_test, y_test = feature_matrix(test_df)
    candidates = train_candidates(x_train, y_train, random_seed=42)
    evaluations = [evaluate_candidate(c, x_test, y_test, test_df) for c in candidates]
    winner = select_winner(evaluations)
    assert winner is not None
    assert winner.metrics["macro_f1"] >= 0.75


def test_model_card_and_checksum_roundtrip(fixture_dir: Path, tmp_path: Path):
    from ml.data.preprocess import preprocess_clip
    from ml.data.schema import Manifest
    from ml.data.split import assign_splits
    from ml.models.train import save_model

    manifest = Manifest.model_validate_json((fixture_dir / "manifest.json").read_text())
    processed = [preprocess_clip(clip, fixture_dir) for clip in manifest.clips]
    assigned = assign_splits(processed, seed=42)
    frame = build_feature_frame(assigned, fixture_dir)
    train_df = frame[frame["split"] == "train"]
    x_train, y_train = feature_matrix(train_df)
    candidate = train_candidates(x_train, y_train)[0]
    model_path = tmp_path / "model.joblib"
    save_model(candidate.pipeline, model_path)
    assert artifact_checksum(model_path)
    loaded = load_pipeline(model_path)
    assert loaded.predict(x_train[:1]).shape == (1,)


@pytest.mark.integration
def test_pipeline_end_to_end(fixture_dir: Path, tmp_path: Path):
    output = tmp_path / "run"
    result = run_pipeline(
        manifest_path=fixture_dir / "manifest.json",
        output_dir=output,
        seed=42,
        tracking_uri="http://localhost:5000",
        register=True,
    )
    assert result["validation_passed"] is True
    assert result["macro_f1"] >= 0.75
    assert Path(result["model_card"]).exists()
    report = json.loads((output / "evaluation_report.json").read_text())
    assert len(report["comparison"]["comparison"]) == 2
