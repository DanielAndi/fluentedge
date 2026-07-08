#!/usr/bin/env python3
"""Verify and optionally run upload retention cleanup (NFR-PRIV-001)."""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.app.services.storage import FilesystemStorage, create_storage_adapter  # noqa: E402


def build_storage():
    backend = os.environ.get("STORAGE_BACKEND", "filesystem")
    return create_storage_adapter(
        backend,
        endpoint_url=os.environ.get("S3_ENDPOINT_URL", "http://localhost:4566"),
        region=os.environ.get("AWS_REGION", "us-west-2"),
        access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
        secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        filesystem_root=os.environ.get("FILESYSTEM_STORAGE_ROOT", str(ROOT / ".local-storage")),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify upload retention cleanup")
    parser.add_argument("--cleanup", action="store_true", help="Delete expired uploads")
    parser.add_argument("--self-test", action="store_true", help="Seed an expired object before cleanup")
    parser.add_argument("--max-age-seconds", type=int, default=None)
    args = parser.parse_args()

    retention_hours = int(os.environ.get("UPLOAD_RETENTION_HOURS", "24"))
    max_age = args.max_age_seconds or retention_hours * 3600
    bucket = os.environ.get("S3_UPLOAD_BUCKET", "fluentedge-uploads")
    storage = build_storage()

    if isinstance(storage, FilesystemStorage) and args.self_test:
        test_key = storage.put_object(bucket, b"retention-test", prefix="uploads")
        test_path = storage._object_path(bucket, test_key)  # noqa: SLF001 - test helper
        old_time = time.time() - max_age - 60
        os.utime(test_path, (old_time, old_time))

    before = storage.list_objects(bucket, "uploads/")
    deleted = storage.cleanup_expired(bucket, prefix="uploads/", max_age_seconds=max_age)
    after = storage.list_objects(bucket, "uploads/")

    print(f"retention_hours={retention_hours}")
    print(f"objects_before={len(before)}")
    print(f"deleted={deleted}")
    print(f"objects_after={len(after)}")
    print(f"checked_at={datetime.now(timezone.utc).isoformat()}")

    if args.cleanup or deleted > 0:
        if deleted == 0 and len(before) > 0:
            print("warning: expected deletions but none occurred")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
