"""SQL Server Implementor using pyodbc.

`pyodbc` is imported lazily inside the methods that need it so the module
can be imported (and unit-tested with mocks) even in environments without
the ODBC driver installed.
"""

from __future__ import annotations

from typing import Any

from data_view.domain.entities import ConnectionConfig, QueryResult, Record
from data_view.domain.interfaces import DataSource, DataSourceError


class SqlServerDataSource(DataSource):
    """Implementor: queries a SQL Server table via pyodbc."""

    def __init__(self, config: ConnectionConfig) -> None:
        self._config = config
        self._connection: Any | None = None

    def connect(self) -> None:
        """Open a pyodbc connection using the injected ConnectionConfig."""
        if self._connection is not None:
            return
        try:
            import pyodbc
        except ImportError as exc:  # pragma: no cover - exercised via mocks
            raise DataSourceError("pyodbc is not installed.") from exc
        driver = self._config.extra.get("driver", "ODBC Driver 17 for SQL Server")
        connection_string = (
            f"DRIVER={{{driver}}};SERVER={self._config.host},{self._config.port};"
            f"DATABASE={self._config.database};UID={self._config.username};"
            f"PWD={self._config.password}"
        )
        try:
            self._connection = pyodbc.connect(connection_string)
        except pyodbc.Error as exc:
            raise DataSourceError(f"SQL Server connection failed: {exc}") from exc

    def disconnect(self) -> None:
        """Close the pyodbc connection if one is open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def fetch(self, collection: str, filters: dict[str, object]) -> QueryResult:
        """Run a parameterized SELECT against `collection` (table name)."""
        if self._connection is None:
            raise DataSourceError("fetch() called before connect().")
        where_clause, params = _build_where_clause(filters)
        query = f"SELECT * FROM {collection}{where_clause}"  # noqa: S608
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            rows = [
                Record(fields=dict(zip(columns, row, strict=True)))
                for row in cursor.fetchall()
            ]
        except Exception as exc:
            raise DataSourceError(f"SQL Server query failed: {exc}") from exc
        finally:
            cursor.close()
        return QueryResult(source_name=self.source_name(), records=rows)

    def source_name(self) -> str:
        """Return the implementor's display name."""
        return "SQL Server"


def _build_where_clause(filters: dict[str, object]) -> tuple[str, list[object]]:
    """Translate a filters dict into a parameterized SQL WHERE clause."""
    if not filters:
        return "", []
    conditions = [f"{key} = ?" for key in filters]
    return " WHERE " + " AND ".join(conditions), list(filters.values())
