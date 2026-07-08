"""Text normalization (FR-DI-005)."""

from __future__ import annotations

import re
import unicodedata

_PUNCT_RE = re.compile(r"[^\w\s']+", re.UNICODE)
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase, collapse whitespace, and strip punctuation."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text
