"""Adapters — bridge each cloud SDK (Adaptee) to CloudStorage (Target).

Three concrete Adapters:
  - S3StorageAdapter   : boto3 S3 client  → CloudStorage
  - GCSStorageAdapter  : FakeGCSClient    → CloudStorage
  - AzureStorageAdapter: FakeAzureClient  → CloudStorage

Each adapter translates the Target method calls into provider-specific SDK
calls, isolating the rest of the codebase from any SDK detail (DIP).

LSP guarantee: every method raises only domain exceptions (StorageError
subclasses), never raw SDK exceptions.  Return types are identical for all
three adapters (str, bytes, None, list[str]).
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

from cloud_adapter.domain.entities import (
    StorageDeleteError,
    StorageDownloadError,
    StorageKeyNotFoundError,
    StorageUploadError,
)
from cloud_adapter.infrastructure.fake_clients import (
    AzureResourceNotFoundError,
    FakeAzureClient,
    FakeGCSClient,
)

if TYPE_CHECKING:
    import types


# ── S3StorageAdapter ──────────────────────────────────────────────────────────


class S3StorageAdapter:
    """Adapter: boto3 S3 client → CloudStorage Target.

    Expects a real (or LocalStack) boto3 S3 client injected at construction.
    All boto3-specific exceptions are translated to domain StorageError types.
    """

    PROVIDER = "s3"

    def __init__(self, s3_client: object, bucket_name: str, endpoint_url: str = "") -> None:
        # s3_client is typed as object to avoid a hard boto3 import at module level
        self._client = s3_client
        self._bucket = bucket_name
        self._endpoint = endpoint_url.rstrip("/")

    def upload(self, key: str, data: bytes) -> str:
        """Put *data* into S3 under *key* and return the object URL."""
        try:
            self._client.put_object(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Key=key,
                Body=data,
            )
        except Exception as exc:
            raise StorageUploadError(self.PROVIDER, str(exc)) from exc
        return self.get_url(key)

    def download(self, key: str) -> bytes:
        """Retrieve the bytes stored under *key*."""
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)  # type: ignore[attr-defined]
            return response["Body"].read()  # type: ignore[no-any-return]
        except Exception as exc:
            msg = str(exc)
            if "NoSuchKey" in msg or "404" in msg:
                raise StorageKeyNotFoundError(self.PROVIDER, key) from exc
            raise StorageDownloadError(self.PROVIDER, msg) from exc

    def delete(self, key: str) -> None:
        """Remove the object under *key* from S3."""
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)  # type: ignore[attr-defined]
        except Exception as exc:
            raise StorageDeleteError(self.PROVIDER, str(exc)) from exc

    def list_keys(self, prefix: str = "") -> list[str]:
        """Return all keys in the bucket that start with *prefix*."""
        try:
            response = self._client.list_objects_v2(  # type: ignore[attr-defined]
                Bucket=self._bucket,
                Prefix=prefix,
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as exc:
            raise StorageDownloadError(self.PROVIDER, str(exc)) from exc

    def get_url(self, key: str) -> str:
        """Return the URL for *key* (LocalStack-compatible)."""
        base = self._endpoint or f"https://{self._bucket}.s3.amazonaws.com"
        return f"{base}/{self._bucket}/{key}"


# ── GCSStorageAdapter ─────────────────────────────────────────────────────────


class GCSStorageAdapter:
    """Adapter: FakeGCSClient (GCS SDK shape) → CloudStorage Target.

    The GCS SDK uses a very different fluent API:
      client.bucket(name).blob(key).upload_from_file(file_obj)
    We translate that chain into the flat CloudStorage interface.
    """

    PROVIDER = "gcs"

    def __init__(self, gcs_client: FakeGCSClient, bucket_name: str) -> None:
        self._client = gcs_client
        self._bucket_name = bucket_name

    def _bucket(self) -> object:
        return self._client.bucket(self._bucket_name)

    def upload(self, key: str, data: bytes) -> str:
        """Upload *data* via the GCS blob API and return a signed URL."""
        try:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(key)
            blob.upload_from_file(io.BytesIO(data), content_type="application/octet-stream")
        except Exception as exc:
            raise StorageUploadError(self.PROVIDER, str(exc)) from exc
        return self.get_url(key)

    def download(self, key: str) -> bytes:
        """Download via the GCS blob API."""
        try:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(key)
            if not blob.exists():
                raise StorageKeyNotFoundError(self.PROVIDER, key)
            return blob.download_as_bytes()
        except StorageKeyNotFoundError:
            raise
        except Exception as exc:
            raise StorageDownloadError(self.PROVIDER, str(exc)) from exc

    def delete(self, key: str) -> None:
        """Delete via the GCS blob API."""
        try:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(key)
            blob.delete()
        except Exception as exc:
            raise StorageDeleteError(self.PROVIDER, str(exc)) from exc

    def list_keys(self, prefix: str = "") -> list[str]:
        """List using GCS bucket.list_blobs() — different from boto3 list_objects_v2."""
        try:
            bucket = self._client.bucket(self._bucket_name)
            blobs = bucket.list_blobs(prefix=prefix)
            return [b.name for b in blobs]
        except Exception as exc:
            raise StorageDownloadError(self.PROVIDER, str(exc)) from exc

    def get_url(self, key: str) -> str:
        """Return a GCS-style signed URL."""
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(key)
        return blob.generate_signed_url()


# ── AzureStorageAdapter ───────────────────────────────────────────────────────


class AzureStorageAdapter:
    """Adapter: FakeAzureClient (Azure SDK shape) → CloudStorage Target.

    The Azure SDK exposes a ContainerClient with upload_blob / download_blob /
    list_blobs / get_blob_client, which are all different from GCS and boto3.
    We translate them into the flat CloudStorage interface.
    """

    PROVIDER = "azure"

    def __init__(self, azure_client: FakeAzureClient, container_name: str) -> None:
        self._client = azure_client
        self._container_name = container_name

    def _container(self) -> object:
        return self._client.get_container_client(self._container_name)

    def upload(self, key: str, data: bytes) -> str:
        """Upload via Azure upload_blob and return the blob URL."""
        try:
            container = self._client.get_container_client(self._container_name)
            container.upload_blob(key, data, overwrite=True)
        except Exception as exc:
            raise StorageUploadError(self.PROVIDER, str(exc)) from exc
        return self.get_url(key)

    def download(self, key: str) -> bytes:
        """Download via Azure download_blob().readall()."""
        try:
            container = self._client.get_container_client(self._container_name)
            downloader = container.download_blob(key)
            return downloader.readall()
        except AzureResourceNotFoundError as exc:
            raise StorageKeyNotFoundError(self.PROVIDER, key) from exc
        except Exception as exc:
            raise StorageDownloadError(self.PROVIDER, str(exc)) from exc

    def delete(self, key: str) -> None:
        """Delete via Azure delete_blob."""
        try:
            container = self._client.get_container_client(self._container_name)
            container.delete_blob(key)
        except Exception as exc:
            raise StorageDeleteError(self.PROVIDER, str(exc)) from exc

    def list_keys(self, prefix: str = "") -> list[str]:
        """List using Azure list_blobs(name_starts_with=...) — different param name."""
        try:
            container = self._client.get_container_client(self._container_name)
            props = container.list_blobs(name_starts_with=prefix)
            return [p.name for p in props]
        except Exception as exc:
            raise StorageDownloadError(self.PROVIDER, str(exc)) from exc

    def get_url(self, key: str) -> str:
        """Return Azure blob URL via get_blob_client().url."""
        container = self._client.get_container_client(self._container_name)
        blob_client = container.get_blob_client(key)
        return blob_client.url
