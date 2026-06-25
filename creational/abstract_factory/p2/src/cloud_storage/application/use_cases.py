"""Application use cases for the Cloud Storage Factory.

The Client role in the Abstract Factory pattern: each use case depends only
on the CloudStorageFactory abstraction — never on AWS, GCS, or Azure SDKs.
This is the Dependency Inversion Principle applied to cloud providers.
"""
from __future__ import annotations

from cloud_storage.domain.entities import (
    ObjectMetadata,
    ObjectNotFoundError,
    SignedUrlResult,
    UploadResult,
)
from cloud_storage.domain.interfaces import CloudStorageFactory

DEFAULT_SIGNED_URL_EXPIRY = 3600  # 1 hour — avoids magic number in callers


class UploadFileUseCase:
    """Upload a file using the injected cloud provider's StorageClient.

    SRP: only handles upload orchestration.
    DIP: depends on CloudStorageFactory (abstraction).
    """

    def __init__(self, factory: CloudStorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str, data: bytes, content_type: str) -> UploadResult:
        """Upload data to the configured provider and return an UploadResult."""
        storage = self._factory.create_storage_client()
        object_identifier = storage.upload(key, data, content_type)
        return UploadResult(
            key=key,
            provider=self._factory.get_provider_name(),
            object_identifier=object_identifier,
            content_type=content_type,
            size_bytes=len(data),
        )


class DownloadFileUseCase:
    """Download a file using the injected cloud provider's StorageClient.

    Raises ObjectNotFoundError (domain exception) instead of propagating
    provider-specific errors — LSP: callers see a consistent interface.
    """

    def __init__(self, factory: CloudStorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str) -> bytes:
        """Download and return raw file bytes for the given key."""
        storage = self._factory.create_storage_client()
        return storage.download(key)


class DeleteFileUseCase:
    """Delete a file using the injected cloud provider's StorageClient."""

    def __init__(self, factory: CloudStorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str) -> None:
        """Remove the object identified by key from the provider."""
        storage = self._factory.create_storage_client()
        storage.delete(key)


class GetSignedUrlUseCase:
    """Generate a time-limited signed URL for an object.

    ISP: uses only the URLSigner product — does not need StorageClient or
    MetadataClient for this operation.
    """

    def __init__(self, factory: CloudStorageFactory) -> None:
        self._factory = factory

    def execute(
        self,
        key: str,
        expires_in_seconds: int = DEFAULT_SIGNED_URL_EXPIRY,
    ) -> SignedUrlResult:
        """Return a SignedUrlResult with the temporary access URL."""
        signer = self._factory.create_url_signer()
        signed_url = signer.sign_url(key, expires_in_seconds)
        return SignedUrlResult(
            key=key,
            provider=self._factory.get_provider_name(),
            signed_url=signed_url,
            expires_in_seconds=expires_in_seconds,
        )


class GetMetadataUseCase:
    """Retrieve metadata for a stored object."""

    def __init__(self, factory: CloudStorageFactory) -> None:
        self._factory = factory

    def execute(self, key: str) -> ObjectMetadata:
        """Return ObjectMetadata for the given key."""
        metadata_client = self._factory.create_metadata_client()
        metadata = metadata_client.get_metadata(key)
        return ObjectMetadata(
            key=key,
            provider=self._factory.get_provider_name(),
            metadata=metadata,
        )
