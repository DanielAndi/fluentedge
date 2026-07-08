"""Audio loading and normalization (FR-DI-001, FR-DI-003)."""

from __future__ import annotations

import io
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

TARGET_SAMPLE_RATE = 16000
MAX_DURATION_SECONDS = 30.0
MAX_FILE_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".wav", ".flac", ".mp3", ".m4a"}


class AudioValidationError(ValueError):
    pass


def load_audio_bytes(data: bytes, original_path: str = "audio.wav") -> tuple[np.ndarray, int]:
    """Decode supported audio bytes to mono float32 waveform."""
    suffix = Path(original_path).suffix.lower()
    if suffix and suffix not in SUPPORTED_EXTENSIONS:
        raise AudioValidationError(f"Unsupported audio type: {suffix}")
    if len(data) > MAX_FILE_BYTES:
        raise AudioValidationError("File exceeds 10 MB limit")
    try:
        waveform, sample_rate = librosa.load(io.BytesIO(data), sr=None, mono=True)
    except Exception as exc:  # noqa: BLE001
        raise AudioValidationError(f"Unable to decode audio: {exc}") from exc
    duration = len(waveform) / float(sample_rate)
    if duration > MAX_DURATION_SECONDS:
        raise AudioValidationError("Audio exceeds 30 second limit")
    return waveform.astype(np.float32), int(sample_rate)


def load_audio_file(path: str | Path) -> tuple[np.ndarray, int]:
    path = Path(path)
    return load_audio_bytes(path.read_bytes(), original_path=path.name)


def normalize_audio(waveform: np.ndarray, sample_rate: int) -> tuple[np.ndarray, int]:
    """Convert to mono 16 kHz PCM float32 (FR-DI-003)."""
    if waveform.ndim > 1:
        waveform = np.mean(waveform, axis=0)
    if sample_rate != TARGET_SAMPLE_RATE:
        waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=TARGET_SAMPLE_RATE)
        sample_rate = TARGET_SAMPLE_RATE
    return waveform.astype(np.float32), sample_rate


def encode_wav_bytes(waveform: np.ndarray, sample_rate: int = TARGET_SAMPLE_RATE) -> bytes:
    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV", subtype="PCM_16")
    return buffer.getvalue()
