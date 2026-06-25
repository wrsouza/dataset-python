"""Domain entities for the Data Source Bridge.

Plain data structures with no knowledge of which concrete data store
produced them — that knowledge lives in the Implementor side of the Bridge
(`infrastructure/`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

Scalar = str | int | float | bool | None


@dataclass(frozen=True)
class Record:
    """A single row/document returned by a data source query."""

    fields: dict[str, Scalar]

    def get(self, field_name: str) -> Scalar:
        """Return a field's value, or None if the field is absent."""
        return self.fields.get(field_name)


@dataclass(frozen=True)
class QueryResult:
    """Outcome of running a query against a data source."""

    source_name: str
    records: list[Record] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True when the query produced no records."""
        return len(self.records) == 0

    def column_names(self) -> list[str]:
        """Return the union of field names across all records, order-preserving."""
        seen: dict[str, None] = {}
        for record in self.records:
            for name in record.fields:
                seen[name] = None
        return list(seen.keys())

    def to_rows(self) -> list[dict[str, Scalar]]:
        """Return records as plain dicts, suitable for tabular rendering."""
        return [record.fields for record in self.records]


@dataclass(frozen=True)
class ConnectionConfig:
    """Connection settings for a concrete data source.

    Fields are a superset covering both SQL Server (host/port/database/
    user/password) and MongoDB (uri/database) so a single value object can
    be reused across implementors.
    """

    host: str
    port: int
    database: str
    username: str = ""
    password: str = ""
    extra: dict[str, str] = field(default_factory=dict)
