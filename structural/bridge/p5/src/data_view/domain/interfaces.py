"""Bridge interfaces: the Implementor side of the pattern.

`DataSource` is the Implementor — it defines the low-level operation
(connecting to a concrete store and running a query). The Abstraction side
(`DataView` in `application/use_cases.py`) holds a reference to a
`DataSource` and delegates the actual querying to it, so the reporting
abstraction and the storage technology can vary independently.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from data_view.domain.entities import QueryResult


class DataSourceError(Exception):
    """Raised when a concrete data source fails to connect or query."""


class DataSource(ABC):
    """Implementor: runs queries against one concrete data store."""

    @abstractmethod
    def connect(self) -> None:
        """Establish the underlying connection. Idempotent."""

    @abstractmethod
    def disconnect(self) -> None:
        """Release the underlying connection. Idempotent."""

    @abstractmethod
    def fetch(self, collection: str, filters: dict[str, object]) -> QueryResult:
        """Run a query against `collection` filtered by `filters`."""

    @abstractmethod
    def source_name(self) -> str:
        """Return a short human-readable name for this data source."""
