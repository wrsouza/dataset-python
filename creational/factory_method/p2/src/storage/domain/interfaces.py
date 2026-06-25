"""Domain interfaces for the File Storage Factory pattern.

Defines the Creator ABC and Product Protocol.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageClient(Protocol):
    """Product interface — all concrete storage clients must satisfy this."""

    def upload(self, key: str, data: bytes) -> str:
        """Upload data and return the storage URL/path.

        Args:
            key: Unique identifier / path for the file.
            data: Raw bytes to store.

        Returns:
            URL or path where the file can be retrieved.
        """
        ...

    def download(self, key: str) -> bytes:
        """Download and return the raw bytes for a given key.

        Raises:
            FileNotFoundError: if the key does not exist.
        """
        ...

    def delete(self, key: str) -> None:
        """Delete the file at the given key.

        Raises:
            FileNotFoundError: if the key does not exist.
        """
        ...

    def list_keys(self, prefix: str = "") -> list[str]:
        """Return all keys matching the given prefix."""
        ...


class StorageFactory(ABC):
    """Creator — declares the factory method subclasses must implement.

    New storage providers are added by creating new ConcreteCreator
    subclasses — no modification to this class required (OCP).
    """

    @abstractmethod
    def create_client(self) -> StorageClient:
        """Factory method: returns the StorageClient for this provider."""
        ...

    def get_provider_name(self) -> str:
        """Return a human-readable provider name."""
        return self.__class__.__name__.replace("StorageFactory", "")
