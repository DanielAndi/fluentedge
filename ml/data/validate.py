"""Dataset validation (FR-DI-004)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ml.data.schema import ClipRecord, Manifest
from ml.features.audio import AudioValidationError, load_audio_file


@dataclass
class ValidationIssue:
    clip_id: str
    category: str
    message: str


@dataclass
class ValidationReport:
    total_rows: int = 0
    valid_rows: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        critical = {i.category for i in self.issues}
        blocking = {"missing_field", "duplicate_clip_id", "duplicate_path", "unreadable_audio"}
        return not (critical & blocking)

    def to_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows,
            "passed": self.passed,
            "issues": [issue.__dict__ for issue in self.issues],
        }


REQUIRED_FIELDS = ("clip_id", "audio_uri", "transcript", "source_release", "manifest_version")


def validate_manifest(manifest: Manifest, base_dir: Path | None = None) -> ValidationReport:
    report = ValidationReport(total_rows=len(manifest.clips))
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    valid: list[ClipRecord] = []

    for clip in manifest.clips:
        missing = [f for f in REQUIRED_FIELDS if not getattr(clip, f)]
        if missing:
            report.issues.append(
                ValidationIssue(clip.clip_id or "<unknown>", "missing_field", f"Missing: {missing}")
            )
            continue
        if clip.clip_id in seen_ids:
            report.issues.append(
                ValidationIssue(clip.clip_id, "duplicate_clip_id", "Duplicate clip_id")
            )
            continue
        seen_ids.add(clip.clip_id)

        audio_path = _resolve_audio_path(clip.audio_uri, base_dir)
        if str(audio_path) in seen_paths:
            report.issues.append(
                ValidationIssue(clip.clip_id, "duplicate_path", f"Duplicate path: {audio_path}")
            )
            continue
        seen_paths.add(str(audio_path))

        if not audio_path.exists():
            report.issues.append(
                ValidationIssue(clip.clip_id, "unreadable_audio", f"Missing file: {audio_path}")
            )
            continue
        try:
            load_audio_file(audio_path)
        except (AudioValidationError, OSError) as exc:
            report.issues.append(
                ValidationIssue(clip.clip_id, "unreadable_audio", str(exc))
            )
            continue

        valid.append(clip)

    report.valid_rows = len(valid)
    return report


def filter_valid_clips(manifest: Manifest, report: ValidationReport) -> list[ClipRecord]:
    invalid_ids = {issue.clip_id for issue in report.issues}
    return [clip for clip in manifest.clips if clip.clip_id not in invalid_ids]


def _resolve_audio_path(audio_uri: str, base_dir: Path | None) -> Path:
    path = Path(audio_uri)
    if path.is_absolute():
        return path
    if base_dir is not None:
        return (base_dir / path).resolve()
    return path.resolve()
