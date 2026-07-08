"""Unit tests for text normalization (FR-DI-005)."""

from ml.features.text import normalize_text


def test_normalize_lowercase_and_whitespace():
    assert normalize_text("  Hello   World  ") == "hello world"


def test_normalize_punctuation():
    assert normalize_text("Hello, world!") == "hello world"
