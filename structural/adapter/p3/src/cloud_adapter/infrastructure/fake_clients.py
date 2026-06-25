"""Fake cloud client SDKs — Adaptees.

These classes simulate the REAL SDK APIs (GCS and Azure) with their
intentionally different interface shapes.  They are the Adaptees that
our Adapters must bridge to the CloudStorage Target.

In production you would import:
  - boto3          (S3)
  - google.cloud.storage  (GCS)
  - azure.storage.blob    (Azure)

Here we ship pure-Python fakes so the project runs without real credentials.
The S3 adapter uses the real boto3 client pointed at LocalStack.
"""

from __future__ import annotations

import hashlib
import io
from urllib.parse import quote


# ── FakeGCSClient — simulates google-cloud-storage Client ────────────────────


class GCSBlob:
    """Simulates google.cloud.storage.blob.Blob."""

    def __init__(self, name: str, bucket: "GCSBucket") -> None:
        self.name = name
        self._bucket = bucket
        self.size: int = 0
        self._data: bytes = b""

    def upload_from_file(self, file_obj: io.BytesIO, content_type: str = "application/octet-stream") -> None:
        """GCS SDK API: upload from a file-like object."""
        self._data = file_obj.read()
        self.size = len(self._data)
        self._bucket._objects[self.name] = self

    def download_as_bytes(self) -> bytes:
        """GCS SDK API: download object as bytes."""
        return self._data

    def generate_signed_url(self, expiration: int = 3600, method: str = "GET") -> str:
        """GCS SDK API: generate a (fake) signed URL."""
        token = hashlib.md5(self.name.encode()).hexdigest()[:8]
        bucket_name = self._bucket.name
        encoded = quote(self.name, safe="")
        return f"https://storage.googleapis.com/{bucket_name}/{encoded}?token={token}"

    def delete(self) -> None:
        """GCS SDK API: delete this blob."""
        self._bucket._objects.pop(self.name, None)

    def exists(self) -> bool:
        return self.name in self._bucket._objects


class GCSBucket:
    """Simulates google.cloud.storage.Bucket."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._objects: dict[str, GCSBlob] = {}

    def blob(self, blob_name: str) -> GCSBlob:
        """GCS SDK API: get or create a Blob handle."""
        if blob_name not in self._objects:
            return GCSBlob(blob_name, self)
        return self._objects[blob_name]

    def list_blobs(self, prefix: str = "") -> list[GCSBlob]:
        """GCS SDK API: list blobs with optional prefix."""
        return [b for name, b in self._objects.items() if name.startswith(prefix)]


class FakeGCSClient:
    """Adaptee: simulates google.cloud.storage.Client.

    Real API (very different from boto3):
      client.bucket(name) -> Bucket
      bucket.blob(name)   -> Blob
      blob.upload_from_file(file_obj)
      blob.download_as_bytes()
      blob.generate_signed_url(expiration)
      bucket.list_blobs(prefix)
      blob.delete()
    """

    def __init__(self, project: str = "fake-project") -> None:
        self.project = project
        self._buckets: dict[str, GCSBucket] = {}

    def bucket(self, bucket_name: str) -> GCSBucket:
        """Return (or create) a Bucket by name."""
        if bucket_name not in self._buckets:
            self._buckets[bucket_name] = GCSBucket(bucket_name)
        return self._buckets[bucket_name]


# ── FakeAzureClient — simulates azure-storage-blob BlobServiceClient ─────────


class AzureBlobProperties:
    """Simulates azure.storage.blob.BlobProperties."""

    def __init__(self, name: str, size: int) -> None:
        self.name = name
        self.size = size


class FakeAzureContainerClient:
    """Simulates azure.storage.blob.ContainerClient."""

    def __init__(self, account: str, container: str) -> None:
        self._account = account
        self._container = container
        self._blobs: dict[str, bytes] = {}

    def upload_blob(self, name: str, data: bytes, overwrite: bool = True) -> None:
        """Azure SDK API: upload bytes as a named blob."""
        self._blobs[name] = data

    def download_blob(self, blob_name: str) -> "FakeAzureDownloader":
        """Azure SDK API: return a downloader for a named blob."""
        if blob_name not in self._blobs:
            # Azure raises ResourceNotFoundError; we raise a compatible stub
            raise AzureResourceNotFoundError(f"BlobNotFound: {blob_name}")
        return FakeAzureDownloader(self._blobs[blob_name])

    def delete_blob(self, blob_name: str) -> None:
        """Azure SDK API: delete a blob by name."""
        self._blobs.pop(blob_name, None)

    def list_blobs(self, name_starts_with: str = "") -> list[AzureBlobProperties]:
        """Azure SDK API: list blobs with optional prefix filter."""
        return [
            AzureBlobProperties(name, len(data))
            for name, data in self._blobs.items()
            if name.startswith(name_starts_with)
        ]

    def get_blob_client(self, blob: str) -> "FakeAzureBlobClient":
        """Azure SDK API: return a BlobClient for URL generation."""
        return FakeAzureBlobClient(self._account, self._container, blob)


class FakeAzureDownloader:
    """Simulates azure.storage.blob.StorageStreamDownloader."""

    def __init__(self, data: bytes) -> None:
        self._data = data

    def readall(self) -> bytes:
        """Azure SDK API: read all bytes from the stream."""
        return self._data


class FakeAzureBlobClient:
    """Simulates azure.storage.blob.BlobClient."""

    def __init__(self, account: str, container: str, blob: str) -> None:
        self._account = account
        self._container = container
        self._blob = blob

    @property
    def url(self) -> str:
        """Azure SDK API: public URL for the blob."""
        return f"https://{self._account}.blob.core.windows.net/{self._container}/{quote(self._blob, safe='')}"


class AzureResourceNotFoundError(Exception):
    """Stub for azure.core.exceptions.ResourceNotFoundError."""


class FakeAzureClient:
    """Adaptee: simulates azure.storage.blob.BlobServiceClient.

    Real API (different from both boto3 and GCS):
      client.get_container_client(container) -> ContainerClient
      container.upload_blob(name, data, overwrite=True)
      container.download_blob(name).readall()
      container.delete_blob(name)
      container.list_blobs(name_starts_with=prefix)
      container.get_blob_client(blob).url
    """

    def __init__(self, account_name: str = "fakeaccount", account_key: str = "fakekey") -> None:
        self.account_name = account_name
        self._containers: dict[str, FakeAzureContainerClient] = {}

    def get_container_client(self, container: str) -> FakeAzureContainerClient:
        """Return (or create) a ContainerClient by name."""
        if container not in self._containers:
            self._containers[container] = FakeAzureContainerClient(
                self.account_name, container
            )
        return self._containers[container]
