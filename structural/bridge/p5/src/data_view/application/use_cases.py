"""Abstraction side of the Bridge pattern plus the use cases that drive it.

`DataView` is the Abstraction: it exposes a stable, high-level API
(`load`) to client code (the Streamlit UI) while delegating the actual
query execution to whichever `DataSource` (Implementor) was injected into
it. Adding a new data source (e.g. PostgreSQL) never requires touching
`DataView` or the use cases below — only a new `DataSource` implementation.
"""

from __future__ import annotations

from data_view.domain.entities import QueryResult
from data_view.domain.interfaces import DataSource


class EmptyCollectionNameError(Exception):
    """Raised when a report is requested without naming a collection/table."""


class DataView:
    """Bridge Abstraction: loads report data using an injected DataSource."""

    def __init__(self, data_source: DataSource) -> None:
        self._data_source = data_source

    def load(self, collection: str, filters: dict[str, object]) -> QueryResult:
        """Delegate query execution to the implementor and return its result."""
        if not collection.strip():
            raise EmptyCollectionNameError("collection name must not be empty.")
        self._data_source.connect()
        try:
            return self._data_source.fetch(collection, filters)
        finally:
            self._data_source.disconnect()

    def source_name(self) -> str:
        """Expose the active data source's name without leaking its type."""
        return self._data_source.source_name()


class SummarizedDataView(DataView):
    """Refined Abstraction: adds a row-count summary on top of DataView.

    Demonstrates that the Bridge lets the Abstraction hierarchy grow
    independently of the Implementor hierarchy (DataSource subclasses).
    """

    def load_with_summary(
        self, collection: str, filters: dict[str, object]
    ) -> tuple[QueryResult, str]:
        """Load data and return it alongside a human-readable summary."""
        result = self.load(collection, filters)
        summary = (
            f"{len(result.records)} registro(s) de '{collection}' "
            f"via {self.source_name()}"
        )
        return result, summary


class LoadReportUseCase:
    """Use case: load a report's data through the configured DataView."""

    def __init__(self, data_view: DataView) -> None:
        self._data_view = data_view

    def execute(self, collection: str, filters: dict[str, object]) -> QueryResult:
        """Run the query and return the resulting QueryResult."""
        return self._data_view.load(collection, filters)


class ListAvailableSourcesUseCase:
    """Use case: list the data source names registered for selection in the UI."""

    def __init__(self, data_views: dict[str, DataView]) -> None:
        self._data_views = data_views

    def execute(self) -> list[str]:
        """Return the registered source labels in insertion order."""
        return list(self._data_views.keys())
