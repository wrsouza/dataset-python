"""Concrete Factories and Concrete Products for the Cloud Storage Factory pattern.

Three provider families:
- AWS (via LocalStack in docker-compose)
- GCS (fake implementation for local development)
- Azure (fake implementation for local development)

OCP: adding a new cloud provider = new ConcreteFactory + ConcreteProducts.
No changes to interfaces, use cases, or FastAPI routes.
"""
from __future__ import annotations

import hashlib
import time
import urllib.parse
from typing import Any

import boto3
from botocore.config import Config

from cloud_storage.domain.entities import ObjectNotFoundError, StorageUploadError
from cloud_storage.domain.interfaces import CloudStorageFactory

# ── AWS Concrete Products (backed by LocalStack) ───────────────────────────────

class AWSS3StorageClient:
    """ConcreteProduct: uses boto3 against LocalStack S3."""

    def __init__(self, s3_client: Any, bucket_name: str) -> None:
        self._s3 = s3_client
        self._bucket = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self._s3.head_bucket(Bucket=self._bucket)
        except Exception:
            self._s3.create_bucket(Bucket=self._bucket)

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        try:
            self._s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
        except Exception as exc:
            raise StorageUploadError(key, str(exc)) from exc
        return f"s3://{self._bucket}/{key}"

    def download(self, key: str) -> bytes:
        try:
            response = self._s3.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()  # type: ignore[no-any-return]
        except self._s3.exceptions.NoSuchKey:
            raise ObjectNotFoundError(key, "aws")
        except Exception as exc:
            raise ObjectNotFoundError(key, "aws") from exc

    def delete(self, key: str) -> None:
        self._s3.delete_object(Bucket=self._bucket, Key=key)


class AWSS3MetadataClient:
    """ConcreteProduct: retrieves S3 object metadata via boto3."""

    def __init__(self, s3_client: Any, bucket_name: str) -> None:
        self._s3 = s3_client
        self._bucket = bucket_name

    def get_metadata(self, key: str) -> dict[str, str]:
        try:
            response = self._s3.head_object(Bucket=self._bucket, Key=key)
            return {
                "content_type": response.get("ContentType", ""),
                "content_length": str(response.get("ContentLength", 0)),
                "last_modified": str(response.get("LastModified", "")),
                "etag": response.get("ETag", "").strip('"'),
            }
        except Exception as exc:
            raise ObjectNotFoundError(key, "aws") from exc

    def list_keys(self, prefix: str) -> list[str]:
        response = self._s3.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
        contents = response.get("Contents", [])
        return [obj["Key"] for obj in contents]


class AWSS3URLSigner:
    """ConcreteProduct: generates pre-signed S3 URLs via boto3."""

    def __init__(self, s3_client: Any, bucket_name: str) -> None:
        self._s3 = s3_client
        self._bucket = bucket_name

    def sign_url(self, key: str, expires_in_seconds: int) -> str:
        return self._s3.generate_presigned_url(  # type: ignore[no-any-return]
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in_seconds,
        )

    def get_provider_name(self) -> str:
        return "aws"


# ── GCS Fake Concrete Products ─────────────────────────────────────────────────

class FakeGCSStorageClient:
    """ConcreteProduct: in-memory GCS fake — satisfies StorageClient Protocol."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}
        self._content_types: dict[str, str] = {}

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        self._store[key] = data
        self._content_types[key] = content_type
        return f"gs://fake-bucket/{key}"

    def download(self, key: str) -> bytes:
        if key not in self._store:
            raise ObjectNotFoundError(key, "gcs")
        return self._store[key]

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class FakeGCSMetadataClient:
    """ConcreteProduct: in-memory GCS metadata fake."""

    def __init__(self, storage: FakeGCSStorageClient) -> None:
        self._storage = storage

    def get_metadata(self, key: str) -> dict[str, str]:
        data = self._storage._store.get(key)
        if data is None:
            raise ObjectNotFoundError(key, "gcs")
        return {
            "content_type": self._storage._content_types.get(key, ""),
            "content_length": str(len(data)),
            "storage_class": "STANDARD",
            "provider": "gcs-fake",
        }

    def list_keys(self, prefix: str) -> list[str]:
        return [k for k in self._storage._store if k.startswith(prefix)]


class FakeGCSURLSigner:
    """ConcreteProduct: generates deterministic fake GCS signed URLs."""

    def sign_url(self, key: str, expires_in_seconds: int) -> str:
        expiry = int(time.time()) + expires_in_seconds
        token = hashlib.md5(f"{key}:{expiry}".encode()).hexdigest()
        encoded_key = urllib.parse.quote(key, safe="")
        return f"https://storage.googleapis.com/fake-bucket/{encoded_key}?X-Goog-Expires={expires_in_seconds}&X-Goog-Signature={token}"

    def get_provider_name(self) -> str:
        return "gcs"


# ── Azure Fake Concrete Products ───────────────────────────────────────────────

class FakeAzureStorageClient:
    """ConcreteProduct: in-memory Azure Blob Storage fake."""

    def __init__(self) -> None:
        self._blobs: dict[str, bytes] = {}
        self._content_types: dict[str, str] = {}

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        self._blobs[key] = data
        self._content_types[key] = content_type
        return f"https://fakeaccount.blob.core.windows.net/fake-container/{key}"

    def download(self, key: str) -> bytes:
        if key not in self._blobs:
            raise ObjectNotFoundError(key, "azure")
        return self._blobs[key]

    def delete(self, key: str) -> None:
        self._blobs.pop(key, None)


class FakeAzureMetadataClient:
    """ConcreteProduct: in-memory Azure metadata fake."""

    def __init__(self, storage: FakeAzureStorageClient) -> None:
        self._storage = storage

    def get_metadata(self, key: str) -> dict[str, str]:
        blob = self._storage._blobs.get(key)
        if blob is None:
            raise ObjectNotFoundError(key, "azure")
        return {
            "content_type": self._storage._content_types.get(key, ""),
            "content_length": str(len(blob)),
            "blob_type": "BlockBlob",
            "provider": "azure-fake",
        }

    def list_keys(self, prefix: str) -> list[str]:
        return [k for k in self._storage._blobs if k.startswith(prefix)]


class FakeAzureURLSigner:
    """ConcreteProduct: generates deterministic fake Azure SAS URLs."""

    def sign_url(self, key: str, expires_in_seconds: int) -> str:
        expiry = int(time.time()) + expires_in_seconds
        sas = hashlib.sha256(f"{key}:{expiry}".encode()).hexdigest()[:32]
        encoded_key = urllib.parse.quote(key, safe="")
        return (
            f"https://fakeaccount.blob.core.windows.net/fake-container/{encoded_key}"
            f"?sv=2021-06-08&se={expiry}&sig={sas}"
        )

    def get_provider_name(self) -> str:
        return "azure"


# ── Concrete Factories ─────────────────────────────────────────────────────────

class AWSStorageFactory(CloudStorageFactory):
    """ConcreteFactory: creates AWS S3 product family using LocalStack."""

    def __init__(
        self,
        endpoint_url: str = "http://localstack:4566",
        bucket_name: str = "app-bucket",
        region: str = "us-east-1",
    ) -> None:
        self._endpoint_url = endpoint_url
        self._bucket_name = bucket_name
        self._region = region

    def _build_s3_client(self) -> Any:
        return boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            region_name=self._region,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            config=Config(signature_version="s3v4"),
        )

    def create_storage_client(self) -> AWSS3StorageClient:
        return AWSS3StorageClient(self._build_s3_client(), self._bucket_name)

    def create_metadata_client(self) -> AWSS3MetadataClient:
        return AWSS3MetadataClient(self._build_s3_client(), self._bucket_name)

    def create_url_signer(self) -> AWSS3URLSigner:
        return AWSS3URLSigner(self._build_s3_client(), self._bucket_name)

    def get_provider_name(self) -> str:
        return "aws"


class GCSStorageFactory(CloudStorageFactory):
    """ConcreteFactory: creates GCS product family (fake for local dev)."""

    def __init__(self) -> None:
        # Shared storage ensures all three products see the same data
        self._shared_storage = FakeGCSStorageClient()

    def create_storage_client(self) -> FakeGCSStorageClient:
        return self._shared_storage

    def create_metadata_client(self) -> FakeGCSMetadataClient:
        return FakeGCSMetadataClient(self._shared_storage)

    def create_url_signer(self) -> FakeGCSURLSigner:
        return FakeGCSURLSigner()

    def get_provider_name(self) -> str:
        return "gcs"


class AzureStorageFactory(CloudStorageFactory):
    """ConcreteFactory: creates Azure Blob Storage product family (fake)."""

    def __init__(self) -> None:
        self._shared_storage = FakeAzureStorageClient()

    def create_storage_client(self) -> FakeAzureStorageClient:
        return self._shared_storage

    def create_metadata_client(self) -> FakeAzureMetadataClient:
        return FakeAzureMetadataClient(self._shared_storage)

    def create_url_signer(self) -> FakeAzureURLSigner:
        return FakeAzureURLSigner()

    def get_provider_name(self) -> str:
        return "azure"


# ── Provider Registry ──────────────────────────────────────────────────────────

_GCS_FACTORY = GCSStorageFactory()
_AZURE_FACTORY = AzureStorageFactory()


def build_factory_for_provider(
    provider: str,
    localstack_url: str = "http://localstack:4566",
) -> CloudStorageFactory:
    """Return the CloudStorageFactory for the given provider name.

    OCP: register new providers by extending this mapping.
    """
    provider_map: dict[str, CloudStorageFactory] = {
        "aws": AWSStorageFactory(endpoint_url=localstack_url),
        "gcs": _GCS_FACTORY,
        "azure": _AZURE_FACTORY,
    }
    factory = provider_map.get(provider.lower())
    if factory is None:
        supported = ", ".join(provider_map.keys())
        raise ValueError(f"Unknown provider '{provider}'. Supported: {supported}")
    return factory
