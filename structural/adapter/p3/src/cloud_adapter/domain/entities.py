"""Domain entities and exceptions for cloud_adapter.

These are pure Python dataclasses — no framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class UploadResult:
    """Value object returned after a successful upload."""

    key: str
    provider: str
    url: str
    size: int


@dataclass
class ObjectInfo:
    """Value object describing a stored object."""

    key: str
    provider: str
    url: str


# ── Domain exceptions ─────────────────────────────────────────────────────────


class StorageError(Exception):
    """Base class for all storage domain errors."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class StorageUploadError(StorageError):
    """Raised when an upload operation fails."""


class StorageDownloadError(StorageError):
    """Raised when a download operation fails (including key-not-found)."""


class StorageDeleteError(StorageError):
    """Raised when a delete operation fails."""


class StorageKeyNotFoundError(StorageDownloadError):
    """Raised when the requested key does not exist."""

    def __init__(self, provider: str, key: str) -> None:
        self.key = key
        super().__init__(provider, f"Key not found: {key}")
