"""Preprocessing and label derivation (FR-DI-003, FR-DI-005, §5.4)."""

from __future__ import annotations

from pathlib import Path

from ml.data.schema import ClipRecord, LabelName
from ml.features.audio import encode_wav_bytes, load_audio_file, normalize_audio
from ml.features.text import normalize_text


def preprocess_clip(clip: ClipRecord, base_dir: Path) -> ClipRecord:
    audio_path = _resolve_path(clip.audio_uri, base_dir)
    waveform, sample_rate = load_audio_file(audio_path)
    waveform, sample_rate = normalize_audio(waveform, sample_rate)
    normalized_transcript = normalize_text(clip.transcript)
    expected = normalize_text(clip.expected_phrase or clip.transcript)
    label, rule = derive_label(normalized_transcript, expected, clip.label_rule)

    return clip.model_copy(
        update={
            "normalized_transcript": normalized_transcript,
            "duration_seconds": len(waveform) / float(sample_rate),
            "sample_rate_hz": sample_rate,
            "label": label,
            "label_rule": rule,
            "expected_phrase": expected,
        }
    )


def write_normalized_audio(clip: ClipRecord, base_dir: Path, output_dir: Path) -> str:
    audio_path = _resolve_path(clip.audio_uri, base_dir)
    waveform, sample_rate = load_audio_file(audio_path)
    waveform, sample_rate = normalize_audio(waveform, sample_rate)
    rel = Path("normalized") / f"{clip.clip_id}.wav"
    out_path = output_dir / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(encode_wav_bytes(waveform, sample_rate))
    return str(rel)


def derive_label(
    normalized_transcript: str,
    expected_phrase: str,
    existing_rule: str | None = None,
) -> tuple[LabelName, str]:
    """Derive pass/needs_review from phrase similarity; never use source_status."""
    rule = existing_rule or "phrase_similarity"
    if normalized_transcript == expected_phrase:
        return LabelName.PASS, rule
    return LabelName.NEEDS_REVIEW, rule


def _resolve_path(uri: str, base_dir: Path) -> Path:
    path = Path(uri)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()
