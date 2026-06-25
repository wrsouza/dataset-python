"""Domain entities for the storage domain."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UploadResult:
    """Value object returned after a successful upload."""

    key: str
    provider: str
    url: str
    size_bytes: int


@dataclass
class FileMetadata:
    """Metadata about a stored file."""

    key: str
    provider: str
    size_bytes: int


class StorageError(Exception):
    """Base exception for storage domain errors."""

    def __init__(self, message: str, provider: str) -> None:
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class FileNotFoundInStorageError(StorageError):
    """Raised when a requested key does not exist in the storage backend."""

    def __init__(self, key: str, provider: str) -> None:
        self.key = key
        super().__init__(f"Key not found: {key}", provider)


class UnsupportedProviderError(Exception):
    """Raised when an unknown provider slug is requested."""

    def __init__(self, provider: str) -> None:
        self.provider = provider
        super().__init__(f"Unsupported storage provider: {provider}")
