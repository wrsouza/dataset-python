"""Domain entities and value objects for the Cloud Storage Factory.

These dataclasses are the data-layer representation — they never import
from infrastructure or application layers (dependency direction flows inward).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadResult:
    """Value object returned after a successful file upload."""

    key: str
    provider: str
    object_identifier: str
    content_type: str
    size_bytes: int

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "provider": self.provider,
            "object_identifier": self.object_identifier,
            "content_type": self.content_type,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class SignedUrlResult:
    """Value object returned after generating a signed URL."""

    key: str
    provider: str
    signed_url: str
    expires_in_seconds: int

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "provider": self.provider,
            "signed_url": self.signed_url,
            "expires_in_seconds": self.expires_in_seconds,
        }


@dataclass(frozen=True)
class ObjectMetadata:
    """Value object representing metadata for a stored object."""

    key: str
    provider: str
    metadata: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "provider": self.provider,
            "metadata": self.metadata,
        }


class ObjectNotFoundError(Exception):
    """Raised when a key does not exist in the provider's storage."""

    def __init__(self, key: str, provider: str) -> None:
        self.key = key
        self.provider = provider
        super().__init__(f"Object '{key}' not found in {provider} storage")


class StorageUploadError(Exception):
    """Raised when an upload operation fails at the provider level."""

    def __init__(self, key: str, reason: str) -> None:
        self.key = key
        self.reason = reason
        super().__init__(f"Failed to upload '{key}': {reason}")
