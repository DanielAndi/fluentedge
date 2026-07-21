"""Split reproducibility tests (FR-DI-006)."""

import pytest

from ml.data.schema import ClipRecord, SplitName
from ml.data.split import assign_splits, manifest_hash


def _clip(clip_id: str, speaker: str) -> ClipRecord:
    return ClipRecord(
        clip_id=clip_id,
        audio_uri=f"{clip_id}.wav",
        transcript="hello",
        speaker_id=speaker,
        source_release="test",
    )


def test_assign_splits_reproducible():
    clips = [_clip(f"c{i}", f"s{i % 3}") for i in range(12)]
    first = assign_splits(clips, seed=42)
    second = assign_splits(clips, seed=42)
    assert [c.split for c in first] == [c.split for c in second]


def test_no_speaker_overlap_between_splits():
    clips = [_clip(f"c{i}", f"speaker_{i % 4}") for i in range(16)]
    assigned = assign_splits(clips, seed=7)
    train_speakers = {c.speaker_id for c in assigned if c.split == SplitName.TRAIN}
    test_speakers = {c.speaker_id for c in assigned if c.split == SplitName.TEST}
    assert train_speakers.isdisjoint(test_speakers)


def test_six_speakers_produce_nonempty_partitions():
    clips = [_clip(f"c{i}", f"speaker_{i}") for i in range(6)]

    assigned = assign_splits(clips, seed=42)
    split_counts = {split: sum(clip.split == split for clip in assigned) for split in SplitName}

    assert split_counts == {
        SplitName.TRAIN: 4,
        SplitName.VALIDATION: 1,
        SplitName.TEST: 1,
    }


def test_rejects_too_few_speakers_for_requested_partitions():
    clips = [_clip("a", "s1"), _clip("b", "s2")]

    with pytest.raises(ValueError, match="At least 3 speaker groups"):
        assign_splits(clips)


def test_manifest_hash_stable():
    clips = [_clip("a", "s1"), _clip("b", "s2"), _clip("c", "s3")]
    assigned = assign_splits(clips, seed=1)
    assert manifest_hash(assigned) == manifest_hash(assigned)
