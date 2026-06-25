"""Interfaces for the subsystems hidden behind MigrationFacade.

Each interface is a single-purpose abstraction (ISP) so the Facade can depend
on abstractions rather than concrete drivers (DIP) — see solid_principles.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, Protocol

from migration.domain.entities import ConnectionConfig, TableSchema

Row = dict[str, object]


class DBConnection(Protocol):
    """Minimal PEP 249 (DB-API 2.0) surface shared by sqlite3/pymysql/psycopg2."""

    def cursor(self) -> Any: ...

    def commit(self) -> None: ...

    def close(self) -> None: ...


class ConnectionFactory(ABC):
    """Opens a DB-API connection for a given dialect — hides driver selection."""

    @abstractmethod
    def connect(self, config: ConnectionConfig) -> DBConnection: ...


class SchemaAnalyzer(ABC):
    """Inspects a source table's columns and row count."""

    @abstractmethod
    def analyze(self, connection: DBConnection, table: str) -> TableSchema: ...


class DataExtractor(ABC):
    """Streams a table's rows in fixed-size batches to bound memory use."""

    @abstractmethod
    def extract_batches(
        self, connection: DBConnection, table: str, batch_size: int
    ) -> Iterator[list[Row]]: ...


class DataTransformer(ABC):
    """Converts extracted rows into a shape the destination dialect accepts."""

    @abstractmethod
    def transform(self, rows: list[Row], schema: TableSchema) -> list[Row]: ...


class DataLoader(ABC):
    """Writes transformed rows into the destination table."""

    @abstractmethod
    def load(self, connection: DBConnection, table: str, rows: list[Row]) -> int: ...
