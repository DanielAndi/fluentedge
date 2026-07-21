"""Reproducible speaker-aware splits (FR-DI-006)."""

from __future__ import annotations

import hashlib
import math
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
    ratios = {
        SplitName.TRAIN: train_ratio,
        SplitName.VALIDATION: validation_ratio,
        SplitName.TEST: test_ratio,
    }
    if train_ratio < 0 or validation_ratio < 0 or test_ratio < -1e-12:
        raise ValueError("train_ratio + validation_ratio must be <= 1.0")
    ratios[SplitName.TEST] = max(0.0, test_ratio)

    groups: dict[str, list[ClipRecord]] = defaultdict(list)
    for clip in clips:
        key = clip.speaker_id or clip.clip_id
        groups[key].append(clip)

    group_keys = sorted(groups.keys())
    rng = random.Random(seed)
    rng.shuffle(group_keys)

    n = len(group_keys)
    requested_splits = [split for split, ratio in ratios.items() if ratio > 0]
    if n < len(requested_splits):
        raise ValueError(
            f"At least {len(requested_splits)} speaker groups are required for nonempty "
            f"partitions; received {n}"
        )

    counts = {
        split: max(1, math.floor(n * ratio)) if ratio > 0 else 0 for split, ratio in ratios.items()
    }
    while sum(counts.values()) < n:
        split = max(
            requested_splits,
            key=lambda name: (n * ratios[name] - counts[name], ratios[name]),
        )
        counts[split] += 1
    while sum(counts.values()) > n:
        reducible = [split for split in requested_splits if counts[split] > 1]
        split = max(
            reducible,
            key=lambda name: (counts[name] - n * ratios[name], counts[name]),
        )
        counts[split] -= 1

    train_end = counts[SplitName.TRAIN]
    val_end = train_end + counts[SplitName.VALIDATION]

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
