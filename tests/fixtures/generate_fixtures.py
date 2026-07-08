"""Generate tiny synthetic audio fixtures for tests (safe to commit)."""

from __future__ import annotations

import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "synthetic"
SAMPLE_RATE = 16000


def write_tone_wav(path: Path, duration: float, frequency: float = 440.0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = int(duration * SAMPLE_RATE)
    audio = [int(16000 * math.sin(2 * math.pi * frequency * i / SAMPLE_RATE)) for i in range(samples)]
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(struct.pack(f"<{len(audio)}h", *audio))


def write_corrupt_file(path: Path) -> None:
    path.write_bytes(b"not-a-valid-audio-file")


def write_long_wav(path: Path, duration: float = 31.0) -> None:
    write_tone_wav(path, duration)


def build_manifest() -> dict:
    clips = []
    phrases = [
        ("the quick brown fox", "the quick brown fox", "pass"),
        ("hello world", "hello world", "pass"),
        ("good morning", "good morning", "pass"),
        ("thank you", "thank you", "pass"),
        ("how are you", "how are you today", "needs_review"),
        ("see you later", "see you soon", "needs_review"),
        ("open the door", "close the door", "needs_review"),
        ("nice to meet you", "nice meeting you", "needs_review"),
    ]
    clip_idx = 0
    for speaker in range(1, 7):
        for phrase_idx, (transcript, expected, label) in enumerate(phrases):
            clip_id = f"clip_{clip_idx:03d}"
            filename = f"{clip_id}.wav"
            write_tone_wav(OUT_DIR / filename, duration=1.5 + (phrase_idx * 0.1), frequency=220 + speaker * 20)
            clips.append(
                {
                    "clip_id": clip_id,
                    "audio_uri": filename,
                    "transcript": transcript,
                    "expected_phrase": expected,
                    "speaker_id": f"speaker_{speaker:02d}",
                    "label": label,
                    "label_rule": f"fixture:{label}",
                    "source_release": "synthetic-fixture-v1",
                    "manifest_version": "1.0.0",
                }
            )
            clip_idx += 1
    return {"manifest_version": "1.0.0", "seed": 42, "clips": clips}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_corrupt_file(OUT_DIR / "corrupt.wav")
    write_long_wav(OUT_DIR / "too_long.wav")
    manifest = build_manifest()
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest['clips'])} clips in {OUT_DIR}")


if __name__ == "__main__":
    main()
