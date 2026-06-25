"""Abstract interfaces for the Cloud Storage Factory pattern.

Defines AbstractFactory and three AbstractProduct families:
StorageClient, MetadataClient, URLSigner.

ISP: each product is a separate Protocol with focused responsibilities,
so clients can depend only on the interface they need.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


# ── AbstractProducts (ISP: each has its own protocol) ─────────────────────────

class StorageClient(Protocol):
    """AbstractProduct: handles binary file upload and download."""

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload data and return the provider-specific object identifier."""
        ...

    def download(self, key: str) -> bytes:
        """Download and return the raw bytes for the given key."""
        ...

    def delete(self, key: str) -> None:
        """Permanently remove the object identified by key."""
        ...


class MetadataClient(Protocol):
    """AbstractProduct: retrieves metadata about stored objects."""

    def get_metadata(self, key: str) -> dict[str, str]:
        """Return a dictionary of metadata fields for the given key."""
        ...

    def list_keys(self, prefix: str) -> list[str]:
        """Return all object keys that start with the given prefix."""
        ...


class URLSigner(Protocol):
    """AbstractProduct: generates pre-signed/temporary access URLs."""

    def sign_url(self, key: str, expires_in_seconds: int) -> str:
        """Return a time-limited URL granting access to the object."""
        ...

    def get_provider_name(self) -> str:
        """Return a human-readable provider identifier."""
        ...


# ── AbstractFactory ────────────────────────────────────────────────────────────

class CloudStorageFactory(ABC):
    """AbstractFactory: creates the three-product family for a cloud provider.

    OCP: new cloud providers are added by subclassing — no existing code changes.
    DIP: FastAPI routes and use cases depend on this abstraction.
    """

    @abstractmethod
    def create_storage_client(self) -> StorageClient:
        """Create the storage client for this provider."""
        ...

    @abstractmethod
    def create_metadata_client(self) -> MetadataClient:
        """Create the metadata client for this provider."""
        ...

    @abstractmethod
    def create_url_signer(self) -> URLSigner:
        """Create the URL signer for this provider."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the human-readable provider name (e.g. 'aws', 'gcs')."""
        ...
