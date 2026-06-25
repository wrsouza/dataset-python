"""Target interface — CloudStorage Protocol.

Defines the unified interface that all cloud storage providers must implement.
Client code (views, use cases) depends ONLY on this abstraction (DIP).
ISP: exactly 5 methods covering one concept — cloud object storage.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class CloudStorage(Protocol):
    """Target: unified cloud storage interface.

    ISP — only storage-relevant methods; no provider-specific details leak out.
    DIP — views and use cases depend on this Protocol, not on boto3/GCS/Azure SDKs.
    LSP — every adapter must honour identical contracts (return types, exceptions).
    """

    def upload(self, key: str, data: bytes) -> str:
        """Upload bytes under *key* and return the public URL."""
        ...

    def download(self, key: str) -> bytes:
        """Download and return the raw bytes stored under *key*."""
        ...

    def delete(self, key: str) -> None:
        """Permanently remove the object identified by *key*."""
        ...

    def list_keys(self, prefix: str = "") -> list[str]:
        """List all object keys that start with *prefix*."""
        ...

    def get_url(self, key: str) -> str:
        """Return the public URL for an existing object without fetching it."""
        ...
