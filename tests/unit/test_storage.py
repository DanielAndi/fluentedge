"""Storage adapter unit tests (FR-INF-003, NFR-SEC-002, NFR-PRIV-001)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

from api.app.services.storage import FilesystemStorage, S3Storage, StorageAdapter


class TestStorageAdapter:
    def test_generate_key_ignores_client_filename(self):
        key = StorageAdapter.generate_key("uploads")
        assert key.startswith("uploads/")
        assert ".." not in key
        assert "/" in key

    def test_generate_key_unique(self):
        keys = {StorageAdapter.generate_key("audio") for _ in range(20)}
        assert len(keys) == 20


class TestFilesystemStorage:
    @pytest.fixture
    def storage(self, tmp_path: Path) -> FilesystemStorage:
        return FilesystemStorage(str(tmp_path))

    def test_put_get_roundtrip(self, storage: FilesystemStorage):
        key = storage.put_object("fluentedge-uploads", b"hello", prefix="uploads")
        assert storage.get_object("fluentedge-uploads", key) == b"hello"

    def test_rejects_path_traversal_on_get(self, storage: FilesystemStorage):
        with pytest.raises(ValueError):
            storage.get_object("bucket", "../etc/passwd")

    def test_bucket_exists(self, storage: FilesystemStorage):
        assert storage.bucket_exists("new-bucket") is True

    def test_cleanup_expired(self, storage: FilesystemStorage, tmp_path: Path):
        key = storage.put_object("fluentedge-uploads", b"old", prefix="uploads")
        path = tmp_path / "fluentedge-uploads" / key
        old = time.time() - 90000
        import os

        os.utime(path, (old, old))
        deleted = storage.cleanup_expired(
            "fluentedge-uploads",
            prefix="uploads/",
            max_age_seconds=3600,
        )
        assert deleted == 1
        assert storage.list_objects("fluentedge-uploads", "uploads/") == []

    def test_list_objects(self, storage: FilesystemStorage):
        storage.put_object("fluentedge-uploads", b"a", prefix="uploads")
        storage.put_object("fluentedge-uploads", b"b", prefix="uploads")
        objects = storage.list_objects("fluentedge-uploads", "uploads/")
        assert len(objects) == 2


class TestS3Storage:
    @pytest.fixture
    def storage(self) -> S3Storage | None:
        endpoint = "http://localhost:4566"
        client = S3Storage(
            endpoint_url=endpoint,
            region="us-west-2",
            access_key_id="test",
            secret_access_key="test",
        )
        try:
            if not client.bucket_exists("fluentedge-uploads"):
                import boto3

                boto3.client(
                    "s3",
                    endpoint_url=endpoint,
                    region_name="us-west-2",
                    aws_access_key_id="test",
                    aws_secret_access_key="test",
                ).create_bucket(
                    Bucket="fluentedge-uploads",
                    CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
                )
        except Exception:
            pytest.skip("LocalStack not available")
        return client

    def test_put_get_delete(self, storage: S3Storage):
        key = storage.put_object("fluentedge-uploads", b"audio-bytes", prefix="uploads")
        assert storage.get_object("fluentedge-uploads", key) == b"audio-bytes"
        storage.delete_object("fluentedge-uploads", key)
        with pytest.raises(ClientError):
            storage.get_object("fluentedge-uploads", key)

    def test_bucket_exists(self, storage: S3Storage):
        assert storage.bucket_exists("fluentedge-uploads") is True
        assert storage.bucket_exists("nonexistent-bucket-xyz") is False
