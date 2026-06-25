"""Domain entities for the Data Migration Facade."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ConnectionConfig:
    """Where to connect — dialect drives which driver the factory picks."""

    dialect: str  # "sqlite" | "mysql" | "postgresql"
    dsn: str


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    data_type: str


@dataclass(frozen=True)
class TableSchema:
    table_name: str
    columns: list[ColumnInfo]
    row_count: int


@dataclass(frozen=True)
class TableMigrationResult:
    table_name: str
    rows_extracted: int
    rows_loaded: int
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class MigrationReport:
    migration_id: str
    tables: list[TableMigrationResult]
    started_at: datetime
    finished_at: datetime

    @property
    def success(self) -> bool:
        return all(table.succeeded for table in self.tables)

    @property
    def total_rows_loaded(self) -> int:
        return sum(table.rows_loaded for table in self.tables)

    @property
    def duration_seconds(self) -> float:
        return (self.finished_at - self.started_at).total_seconds()


@dataclass(frozen=True)
class ValidationIssue:
    table_name: str
    message: str
    severity: str  # "warning" | "error"


@dataclass(frozen=True)
class ValidationReport:
    tables_checked: list[str]
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)
