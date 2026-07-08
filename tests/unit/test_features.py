"""Feature extraction tests (FR-DI-007)."""

from pathlib import Path

import pytest

from ml.data.preprocess import preprocess_clip
from ml.data.schema import Manifest
from ml.data.split import assign_splits
from ml.features.build import build_feature_frame, feature_matrix


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "synthetic"


def test_feature_schema_complete(fixture_dir: Path):
    manifest = Manifest.model_validate_json((fixture_dir / "manifest.json").read_text())
    processed = [preprocess_clip(clip, fixture_dir) for clip in manifest.clips]
    assigned = assign_splits(processed, seed=42)
    frame = build_feature_frame(assigned, fixture_dir)
    assert frame["wer"].notna().all()
    assert frame["mfcc_mean"].notna().all()
    matrix, labels = feature_matrix(frame[frame["split"] == "train"])
    assert matrix.shape[0] == labels.shape[0]
    assert matrix.shape[1] == 9
