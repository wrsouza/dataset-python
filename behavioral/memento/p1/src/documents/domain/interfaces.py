"""Domain interfaces for the Document Version History system.

Defines the Memento pattern contracts: Originator, Memento, and Caretaker.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class MementoProtocol(Protocol):
    """Memento protocol — snapshot is immutable and self-describing."""

    @property
    def version(self) -> int: ...

    @property
    def author(self) -> str: ...


class DocumentOriginator(ABC):
    """Originator ABC — knows how to create and restore from snapshots."""

    @abstractmethod
    def create_snapshot(self) -> "MementoProtocol":
        """Capture current state into an immutable snapshot."""
        ...

    @abstractmethod
    def restore(self, memento: "MementoProtocol") -> None:
        """Restore state from a previously captured snapshot."""
        ...


class DocumentCaretaker(ABC):
    """Caretaker ABC — manages the lifecycle of mementos.

    SRP: only stores/retrieves mementos, has no knowledge of document content.
    OCP: new storage backends extend this without modifying existing code.
    """

    @abstractmethod
    async def save(self, document_id: str, memento: "MementoProtocol") -> None:
        """Persist a memento for a given document."""
        ...

    @abstractmethod
    async def get(self, document_id: str, version: int) -> "MementoProtocol":
        """Retrieve a specific version snapshot."""
        ...

    @abstractmethod
    async def undo(self, document_id: str) -> "MementoProtocol":
        """Return the previous snapshot (one step back)."""
        ...

    @abstractmethod
    async def list_versions(self, document_id: str) -> list["MementoProtocol"]:
        """Return all snapshots for a document, ordered by version."""
        ...
