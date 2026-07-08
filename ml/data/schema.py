"""Canonical dataset schema (FR-DI-004, design spec §5.3)."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SplitName(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


class LabelName(StrEnum):
    PASS = "pass"
    NEEDS_REVIEW = "needs_review"


FEATURE_SCHEMA_VERSION = "1.0.0"
MANIFEST_VERSION = "1.0.0"


class ClipRecord(BaseModel):
    clip_id: str
    audio_uri: str
    transcript: str
    normalized_transcript: str = ""
    split: SplitName | Literal[""] = ""
    label: LabelName | Literal[""] = ""
    duration_seconds: float = 0.0
    sample_rate_hz: int = 0
    speaker_id: str | None = None
    locale: str | None = None
    accent: str | None = None
    source_release: str = "synthetic-fixture-v1"
    source_status: str | None = None  # not used as model feature (leakage guard)
    manifest_version: str = MANIFEST_VERSION
    expected_phrase: str | None = None
    label_rule: str | None = None


class Manifest(BaseModel):
    manifest_version: str = MANIFEST_VERSION
    seed: int = 42
    clips: list[ClipRecord] = Field(default_factory=list)
