"""Feature matrix construction (FR-DI-007)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from jiwer import cer, wer

from ml.data.schema import FEATURE_SCHEMA_VERSION, ClipRecord
from ml.features.audio import load_audio_file, normalize_audio
from ml.features.text import normalize_text

FEATURE_COLUMNS = [
    "transcript_similarity",
    "wer",
    "cer",
    "duration_seconds",
    "speech_rate",
    "mfcc_mean",
    "mfcc_std",
    "rms_energy",
    "silence_ratio",
]


def transcript_similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    a_tokens = a.split()
    b_tokens = b.split()
    overlap = len(set(a_tokens) & set(b_tokens))
    return overlap / max(len(set(a_tokens) | set(b_tokens)), 1)


def extract_clip_features(clip: ClipRecord, base_dir: Path) -> dict[str, float]:
    audio_path = _resolve_path(clip.audio_uri, base_dir)
    waveform, sample_rate = load_audio_file(audio_path)
    waveform, sample_rate = normalize_audio(waveform, sample_rate)

    import librosa

    expected = normalize_text(clip.expected_phrase or clip.transcript)
    observed = clip.normalized_transcript or normalize_text(clip.transcript)
    duration = len(waveform) / float(sample_rate)
    word_count = max(len(observed.split()), 1)
    speech_rate = word_count / max(duration, 0.1)
    mfcc = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=13)
    rms = float(np.sqrt(np.mean(np.square(waveform))))
    silence_ratio = float(np.mean(np.abs(waveform) < 0.01))

    return {
        "clip_id": clip.clip_id,
        "label": clip.label,
        "split": clip.split,
        "transcript_similarity": transcript_similarity(observed, expected),
        "wer": float(wer(expected, observed)) if expected else 0.0,
        "cer": float(cer(expected, observed)) if expected else 0.0,
        "duration_seconds": duration,
        "speech_rate": speech_rate,
        "mfcc_mean": float(np.mean(mfcc)),
        "mfcc_std": float(np.std(mfcc)),
        "rms_energy": rms,
        "silence_ratio": silence_ratio,
    }


def build_feature_frame(clips: list[ClipRecord], base_dir: Path) -> pd.DataFrame:
    rows = [extract_clip_features(clip, base_dir) for clip in clips]
    frame = pd.DataFrame(rows)
    frame.attrs["feature_schema_version"] = FEATURE_SCHEMA_VERSION
    return frame


def feature_matrix(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    labels = (frame["label"] == "pass").astype(int).to_numpy()
    matrix = frame[FEATURE_COLUMNS].astype(float).to_numpy()
    return matrix, labels


def _resolve_path(uri: str, base_dir: Path) -> Path:
    path = Path(uri)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()
