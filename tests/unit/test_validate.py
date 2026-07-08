"""Validation tests (FR-DI-004)."""

from pathlib import Path

import numpy as np
import pytest

from ml.data.schema import ClipRecord, Manifest
from ml.data.validate import validate_manifest
from ml.features.audio import encode_wav_bytes


@pytest.fixture
def fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "synthetic"


def test_validate_synthetic_manifest(fixture_dir: Path):
    manifest = Manifest.model_validate_json((fixture_dir / "manifest.json").read_text())
    report = validate_manifest(manifest, base_dir=fixture_dir)
    assert report.passed
    assert report.valid_rows == len(manifest.clips)


def test_detect_duplicate_clip_id(fixture_dir: Path, tmp_path: Path):
    audio = encode_wav_bytes(np.random.randn(16000).astype(np.float32) * 0.1, 16000)
    wav = tmp_path / "a.wav"
    wav.write_bytes(audio)
    manifest = Manifest(
        clips=[
            ClipRecord(
                clip_id="dup",
                audio_uri=str(wav),
                transcript="hello",
                source_release="test",
            ),
            ClipRecord(
                clip_id="dup",
                audio_uri=str(wav),
                transcript="hello",
                source_release="test",
            ),
        ]
    )
    report = validate_manifest(manifest, base_dir=tmp_path)
    assert not report.passed
    assert any(i.category == "duplicate_clip_id" for i in report.issues)


def test_detect_missing_transcript(fixture_dir: Path, tmp_path: Path):
    audio = encode_wav_bytes(np.random.randn(16000).astype(np.float32) * 0.1, 16000)
    wav = tmp_path / "b.wav"
    wav.write_bytes(audio)
    manifest = Manifest(
        clips=[
            ClipRecord(
                clip_id="missing",
                audio_uri=str(wav),
                transcript="",
                source_release="test",
            )
        ]
    )
    report = validate_manifest(manifest, base_dir=tmp_path)
    assert any(i.category == "missing_field" for i in report.issues)


def test_corrupt_audio_rejected(fixture_dir: Path):
    manifest = Manifest(
        clips=[
            ClipRecord(
                clip_id="corrupt",
                audio_uri="corrupt.wav",
                transcript="hello",
                source_release="test",
            )
        ]
    )
    report = validate_manifest(manifest, base_dir=fixture_dir)
    assert any(i.category == "unreadable_audio" for i in report.issues)
