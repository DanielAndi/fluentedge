"""Storage adapter interface and implementations (FR-INF-003, NFR-SEC-002, NFR-PRIV-001)."""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError
from ulid import ULID


class StorageAdapter(ABC):
    """S3-compatible storage interface with generated object keys."""

    @abstractmethod
    def put_object(
        self,
        bucket: str,
        data: bytes | BinaryIO,
        *,
        prefix: str = "uploads",
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Store data and return a generated object key."""

    @abstractmethod
    def get_object(self, bucket: str, key: str) -> bytes:
        """Retrieve object bytes."""

    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> None:
        """Delete a single object."""

    @abstractmethod
    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:
        """List objects with key and last_modified metadata."""

    @abstractmethod
    def bucket_exists(self, bucket: str) -> bool:
        """Return True if the bucket is reachable."""

    @abstractmethod
    def cleanup_expired(
        self,
        bucket: str,
        *,
        prefix: str = "uploads/",
        max_age_seconds: int,
    ) -> int:
        """Delete objects older than max_age_seconds. Returns count deleted."""

    @staticmethod
    def generate_key(prefix: str = "uploads") -> str:
        """Generate a safe object key; never use client filenames (NFR-SEC-002)."""
        safe_prefix = prefix.strip("/")
        return f"{safe_prefix}/{ULID()}" if safe_prefix else str(ULID())


class S3Storage(StorageAdapter):
    """S3-compatible storage via boto3 endpoint configuration."""

    def __init__(
        self,
        *,
        endpoint_url: str,
        region: str,
        access_key_id: str,
        secret_access_key: str,
    ) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def put_object(
        self,
        bucket: str,
        data: bytes | BinaryIO,
        *,
        prefix: str = "uploads",
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        key = self.generate_key(prefix)
        body = data if isinstance(data, bytes) else data.read()
        extra: dict = {"ContentType": content_type}
        if metadata:
            extra["Metadata"] = metadata
        self._client.put_object(Bucket=bucket, Key=key, Body=body, **extra)
        return key

    def get_object(self, bucket: str, key: str) -> bytes:
        response = self._client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    def delete_object(self, bucket: str, key: str) -> None:
        self._client.delete_object(Bucket=bucket, Key=key)

    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:
        paginator = self._client.get_paginator("list_objects_v2")
        objects: list[dict] = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                objects.append(
                    {
                        "key": item["Key"],
                        "last_modified": item["LastModified"],
                        "size": item["Size"],
                    }
                )
        return objects

    def bucket_exists(self, bucket: str) -> bool:
        try:
            self._client.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            return False

    def cleanup_expired(
        self,
        bucket: str,
        *,
        prefix: str = "uploads/",
        max_age_seconds: int,
    ) -> int:
        cutoff = time.time() - max_age_seconds
        deleted = 0
        for obj in self.list_objects(bucket, prefix):
            last_modified = obj["last_modified"]
            if last_modified.timestamp() < cutoff:
                self.delete_object(bucket, obj["key"])
                deleted += 1
        return deleted


class FilesystemStorage(StorageAdapter):
    """Local filesystem fallback when LocalStack is unavailable."""

    def __init__(self, root: str) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _bucket_path(self, bucket: str) -> Path:
        path = self._root / bucket
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _object_path(self, bucket: str, key: str) -> Path:
        # Reject path traversal (NFR-SEC-002)
        normalized = Path(key)
        if normalized.is_absolute() or ".." in normalized.parts:
            raise ValueError("Invalid object key")
        return self._bucket_path(bucket) / normalized

    def put_object(
        self,
        bucket: str,
        data: bytes | BinaryIO,
        *,
        prefix: str = "uploads",
        content_type: str = "application/octet-stream",
        metadata: dict[str, str] | None = None,
    ) -> str:
        key = self.generate_key(prefix)
        path = self._object_path(bucket, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        body = data if isinstance(data, bytes) else data.read()
        path.write_bytes(body)
        meta_path = path.with_suffix(path.suffix + ".meta")
        meta_lines = [f"content_type={content_type}"]
        if metadata:
            for k, v in metadata.items():
                meta_lines.append(f"{k}={v}")
        meta_lines.append(f"last_modified={datetime.now(timezone.utc).isoformat()}")
        meta_path.write_text("\n".join(meta_lines), encoding="utf-8")
        return key

    def get_object(self, bucket: str, key: str) -> bytes:
        return self._object_path(bucket, key).read_bytes()

    def delete_object(self, bucket: str, key: str) -> None:
        path = self._object_path(bucket, key)
        if path.exists():
            path.unlink()
        meta_path = path.with_suffix(path.suffix + ".meta")
        if meta_path.exists():
            meta_path.unlink()

    def list_objects(self, bucket: str, prefix: str = "") -> list[dict]:
        base = self._bucket_path(bucket)
        search = base / prefix if prefix else base
        objects: list[dict] = []
        if not search.exists():
            return objects
        for path in search.rglob("*"):
            if path.is_file() and not path.name.endswith(".meta"):
                rel = path.relative_to(base).as_posix()
                stat = path.stat()
                objects.append(
                    {
                        "key": rel,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                        "size": stat.st_size,
                    }
                )
        return objects

    def bucket_exists(self, bucket: str) -> bool:
        return self._bucket_path(bucket).exists()

    def cleanup_expired(
        self,
        bucket: str,
        *,
        prefix: str = "uploads/",
        max_age_seconds: int,
    ) -> int:
        cutoff = time.time() - max_age_seconds
        deleted = 0
        for obj in self.list_objects(bucket, prefix):
            if obj["last_modified"].timestamp() < cutoff:
                self.delete_object(bucket, obj["key"])
                deleted += 1
        return deleted


def create_storage_adapter(
    backend: str,
    *,
    endpoint_url: str,
    region: str,
    access_key_id: str,
    secret_access_key: str,
    filesystem_root: str,
) -> StorageAdapter:
    """Factory for environment-based storage selection (FR-INF-003)."""
    if backend == "filesystem":
        return FilesystemStorage(filesystem_root)
    return S3Storage(
        endpoint_url=endpoint_url,
        region=region,
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
    )
