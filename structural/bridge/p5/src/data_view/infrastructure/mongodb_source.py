"""MongoDB Implementor using pymongo.

`pymongo` is imported lazily so this module can be imported (and unit
tested with mongomock or unittest.mock) without the real driver installed.
"""

from __future__ import annotations

from typing import Any

from data_view.domain.entities import ConnectionConfig, QueryResult, Record
from data_view.domain.interfaces import DataSource, DataSourceError


class MongoDataSource(DataSource):
    """Implementor: queries a MongoDB collection via pymongo."""

    def __init__(self, config: ConnectionConfig) -> None:
        self._config = config
        self._client: Any | None = None

    def connect(self) -> None:
        """Open a pymongo client using the injected ConnectionConfig."""
        if self._client is not None:
            return
        try:
            from pymongo import MongoClient
        except ImportError as exc:  # pragma: no cover - exercised via mocks
            raise DataSourceError("pymongo is not installed.") from exc
        uri = self._config.extra.get("uri") or (
            f"mongodb://{self._config.username}:{self._config.password}@"
            f"{self._config.host}:{self._config.port}"
        )
        self._client = MongoClient(uri)

    def disconnect(self) -> None:
        """Close the pymongo client if one is open."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def fetch(self, collection: str, filters: dict[str, object]) -> QueryResult:
        """Run a `find` against `collection` filtered by `filters`."""
        if self._client is None:
            raise DataSourceError("fetch() called before connect().")
        try:
            database = self._client[self._config.database]
            documents = list(database[collection].find(filters))
        except Exception as exc:
            raise DataSourceError(f"MongoDB query failed: {exc}") from exc
        records = [Record(fields=_strip_object_id(doc)) for doc in documents]
        return QueryResult(source_name=self.source_name(), records=records)

    def source_name(self) -> str:
        """Return the implementor's display name."""
        return "MongoDB"


def _strip_object_id(document: dict[str, Any]) -> dict[str, Any]:
    """Drop the non-serializable `_id` ObjectId, keeping it as a string."""
    fields = dict(document)
    if "_id" in fields:
        fields["_id"] = str(fields["_id"])
    return fields
