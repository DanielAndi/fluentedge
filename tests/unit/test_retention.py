"""Retention cleanup tests (NFR-PRIV-001)."""

from __future__ import annotations

import os
import time
from pathlib import Path

from api.app.services.storage import FilesystemStorage


def test_verify_retention_script_logic(tmp_path: Path):
    root = tmp_path / "storage"
    storage = FilesystemStorage(str(root))
    bucket = "fluentedge-uploads"
    key = storage.put_object(bucket, b"demo", prefix="uploads")
    path = root / bucket / key
    old = time.time() - 100000
    os.utime(path, (old, old))
    deleted = storage.cleanup_expired(bucket, prefix="uploads/", max_age_seconds=3600)
    assert deleted == 1
