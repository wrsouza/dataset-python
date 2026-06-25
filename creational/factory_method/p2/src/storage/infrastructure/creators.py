"""ConcreteCreators and ConcreteProducts for each storage provider.

S3StorageFactory  -> S3StorageClient  (LocalStack)
GCSStorageFactory -> GCSStorageClient (fake in-memory)
LocalStorageFactory -> LocalStorageClient (filesystem)
"""
from __future__ import annotations

import io
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from storage.domain.entities import FileNotFoundInStorageError, StorageError
from storage.domain.interfaces import StorageClient, StorageFactory


# ── S3 (LocalStack) ──────────────────────────────────────────────────────────

class S3StorageClient:
    """ConcreteProduct — AWS S3 compatible client (LocalStack in development)."""

    def __init__(self, bucket: str, endpoint_url: str) -> None:
        self._bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload(self, key: str, data: bytes) -> str:
        try:
            self._client.put_object(Bucket=self._bucket, Key=key, Body=data)
            endpoint = self._client.meta.endpoint_url or "https://s3.amazonaws.com"
            return f"{endpoint}/{self._bucket}/{key}"
        except ClientError as exc:
            raise StorageError(str(exc), "S3") from exc

    def download(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("NoSuchKey", "404"):
                raise FileNotFoundInStorageError(key, "S3") from exc
            raise StorageError(str(exc), "S3") from exc

    def delete(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            raise StorageError(str(exc), "S3") from exc

    def list_keys(self, prefix: str = "") -> list[str]:
        try:
            paginator = self._client.get_paginator("list_objects_v2")
            keys: list[str] = []
            for page in paginator.paginate(Bucket=self._bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])
            return keys
        except ClientError as exc:
            raise StorageError(str(exc), "S3") from exc


class S3StorageFactory(StorageFactory):
    """ConcreteCreator — creates an S3StorageClient pointing at LocalStack."""

    def __init__(
        self,
        bucket: str | None = None,
        endpoint_url: str | None = None,
    ) -> None:
        self._bucket = bucket or os.getenv("S3_BUCKET", "app-files")
        self._endpoint_url = endpoint_url or os.getenv(
            "AWS_ENDPOINT_URL", "http://localstack:4566"
        )

    def create_client(self) -> StorageClient:
        return S3StorageClient(  # type: ignore[return-value]
            bucket=self._bucket,
            endpoint_url=self._endpoint_url,
        )

    def get_provider_name(self) -> str:
        return "S3"


# ── GCS (fake in-memory) ──────────────────────────────────────────────────────

class GCSStorageClient:
    """ConcreteProduct — fake GCS client backed by an in-memory dict.

    A real implementation would use google-cloud-storage, but for the
    purposes of this educational dataset we fake it so no GCP credentials
    are required (OCP: swappable with a real client).
    """

    # Shared in-process store to simulate a persistent bucket
    _store: dict[str, bytes] = {}

    def __init__(self, bucket: str) -> None:
        self._bucket = bucket

    def _key(self, key: str) -> str:
        return f"{self._bucket}/{key}"

    def upload(self, key: str, data: bytes) -> str:
        self._store[self._key(key)] = data
        return f"gs://{self._bucket}/{key}"

    def download(self, key: str) -> bytes:
        full_key = self._key(key)
        if full_key not in self._store:
            raise FileNotFoundInStorageError(key, "GCS")
        return self._store[full_key]

    def delete(self, key: str) -> None:
        full_key = self._key(key)
        if full_key not in self._store:
            raise FileNotFoundInStorageError(key, "GCS")
        del self._store[full_key]

    def list_keys(self, prefix: str = "") -> list[str]:
        bucket_prefix = f"{self._bucket}/"
        return [
            k.removeprefix(bucket_prefix)
            for k in self._store
            if k.startswith(bucket_prefix) and k.removeprefix(bucket_prefix).startswith(prefix)
        ]


class GCSStorageFactory(StorageFactory):
    """ConcreteCreator — creates a GCSStorageClient (fake for dev/test)."""

    def __init__(self, bucket: str | None = None) -> None:
        self._bucket = bucket or os.getenv("GCS_BUCKET", "app-files-gcs")

    def create_client(self) -> StorageClient:
        return GCSStorageClient(bucket=self._bucket)  # type: ignore[return-value]

    def get_provider_name(self) -> str:
        return "GCS"


# ── Local Filesystem ──────────────────────────────────────────────────────────

class LocalStorageClient:
    """ConcreteProduct — stores files on the local filesystem."""

    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)
        self._base.mkdir(parents=True, exist_ok=True)

    def upload(self, key: str, data: bytes) -> str:
        dest = self._base / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return f"file://{dest.resolve()}"

    def download(self, key: str) -> bytes:
        dest = self._base / key
        if not dest.exists():
            raise FileNotFoundInStorageError(key, "Local")
        return dest.read_bytes()

    def delete(self, key: str) -> None:
        dest = self._base / key
        if not dest.exists():
            raise FileNotFoundInStorageError(key, "Local")
        dest.unlink()

    def list_keys(self, prefix: str = "") -> list[str]:
        return [
            str(p.relative_to(self._base))
            for p in self._base.rglob("*")
            if p.is_file() and str(p.relative_to(self._base)).startswith(prefix)
        ]


class LocalStorageFactory(StorageFactory):
    """ConcreteCreator — creates a LocalStorageClient."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = base_dir or os.getenv("LOCAL_STORAGE_DIR", "/tmp/app-files")

    def create_client(self) -> StorageClient:
        return LocalStorageClient(base_dir=self._base_dir)  # type: ignore[return-value]

    def get_provider_name(self) -> str:
        return "Local"


# ── Registry ──────────────────────────────────────────────────────────────────

PROVIDER_REGISTRY: dict[str, StorageFactory] = {
    "s3": S3StorageFactory(),
    "gcs": GCSStorageFactory(),
    "local": LocalStorageFactory(),
}
