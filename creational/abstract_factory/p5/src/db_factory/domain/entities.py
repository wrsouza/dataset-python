"""Domain entities and value objects for the Database Connector Factory.

These dataclasses travel across layer boundaries without carrying
any database-specific types — they are pure Python data containers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


class QueryExecutionError(Exception):
    """Raised when a database query fails.

    Wraps the engine-specific exception so that upper layers never depend
    on psycopg2, mysql-connector, or pyodbc exception hierarchies.
    """

    def __init__(self, engine: str, sql: str, reason: str) -> None:
        self.engine = engine
        self.sql = sql
        self.reason = reason
        super().__init__(f"[{engine}] Query failed: {reason}")


class ConnectionError(Exception):  # noqa: A001 — intentional domain shadow
    """Raised when a database connection cannot be established."""

    def __init__(self, engine: str, reason: str) -> None:
        self.engine = engine
        self.reason = reason
        super().__init__(f"[{engine}] Connection failed: {reason}")


@dataclass(frozen=True)
class HealthCheckResult:
    """Value object representing the result of a database health check."""

    engine: str
    is_healthy: bool
    checked_at: datetime = field(default_factory=datetime.utcnow)
    connection_info: dict[str, str] = field(default_factory=dict)
    error_message: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "engine": self.engine,
            "is_healthy": self.is_healthy,
            "checked_at": self.checked_at.isoformat(),
            "connection_info": self.connection_info,
            "error_message": self.error_message,
        }


@dataclass(frozen=True)
class QueryResult:
    """Value object wrapping the rows returned by a QueryBuilder.execute() call."""

    engine: str
    sql: str
    rows: list[dict[str, object]]
    row_count: int
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "engine": self.engine,
            "sql": self.sql,
            "row_count": self.row_count,
            "rows": self.rows,
            "executed_at": self.executed_at.isoformat(),
        }


@dataclass(frozen=True)
class MigrationReport:
    """Value object representing the outcome of a migration run."""

    engine: str
    applied: list[str]
    pending_before: int
    ran_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict for JSON HTTP responses."""
        return {
            "engine": self.engine,
            "applied_count": len(self.applied),
            "applied": self.applied,
            "ran_at": self.ran_at.isoformat(),
        }
