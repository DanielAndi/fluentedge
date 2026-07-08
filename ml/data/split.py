"""Reproducible speaker-aware splits (FR-DI-006)."""

from __future__ import annotations

import hashlib
import random
from collections import defaultdict

from ml.data.schema import ClipRecord, SplitName


def assign_splits(
    clips: list[ClipRecord],
    *,
    seed: int = 42,
    train_ratio: float = 0.7,
    validation_ratio: float = 0.15,
) -> list[ClipRecord]:
    test_ratio = 1.0 - train_ratio - validation_ratio
    if test_ratio < 0:
        raise ValueError("train_ratio + validation_ratio must be <= 1.0")

    groups: dict[str, list[ClipRecord]] = defaultdict(list)
    for clip in clips:
        key = clip.speaker_id or clip.clip_id
        groups[key].append(clip)

    group_keys = sorted(groups.keys())
    rng = random.Random(seed)
    rng.shuffle(group_keys)

    n = len(group_keys)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * validation_ratio)

    split_map: dict[str, SplitName] = {}
    for idx, key in enumerate(group_keys):
        if idx < train_end:
            split_map[key] = SplitName.TRAIN
        elif idx < val_end:
            split_map[key] = SplitName.VALIDATION
        else:
            split_map[key] = SplitName.TEST

    updated: list[ClipRecord] = []
    for clip in clips:
        key = clip.speaker_id or clip.clip_id
        updated.append(clip.model_copy(update={"split": split_map[key]}))
    return updated


def manifest_hash(clips: list[ClipRecord]) -> str:
    payload = "|".join(
        sorted(f"{c.clip_id}:{c.audio_uri}:{c.normalized_transcript}:{c.split}" for c in clips)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
