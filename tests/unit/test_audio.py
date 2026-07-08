"""Unit tests for audio validation (FR-DI-001, FR-DI-002, FR-DI-003)."""

from pathlib import Path

import numpy as np
import pytest

from ml.features.audio import (
    AudioValidationError,
    encode_wav_bytes,
    load_audio_bytes,
    normalize_audio,
)


def test_normalize_to_16k_mono():
    waveform = np.random.randn(8000).astype(np.float32)
    normalized, rate = normalize_audio(waveform, 8000)
    assert rate == 16000
    assert normalized.ndim == 1


def test_reject_oversized_payload():
    with pytest.raises(AudioValidationError):
        load_audio_bytes(b"x" * (10 * 1024 * 1024 + 1))


def test_valid_wav_roundtrip(tmp_path: Path):
    waveform = np.random.randn(16000).astype(np.float32) * 0.1
    data = encode_wav_bytes(waveform, 16000)
    decoded, rate = load_audio_bytes(data, "clip.wav")
    assert rate == 16000
    assert len(decoded) > 0


def test_reject_unsupported_extension():
    with pytest.raises(AudioValidationError):
        load_audio_bytes(b"abc", "clip.xyz")
