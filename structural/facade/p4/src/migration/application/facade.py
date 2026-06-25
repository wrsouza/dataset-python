"""MigrationFacade — the single entry point hiding 6 migration subsystems.

Client code (the CLI) only ever calls migrate()/dry_run()/rollback(). It never
touches SchemaAnalyzer, DataExtractor, DataTransformer, DataLoader,
MigrationReporter, or RollbackManager directly — that is the Facade pattern.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from migration.domain.entities import (
    ConnectionConfig,
    MigrationReport,
    TableMigrationResult,
    ValidationIssue,
    ValidationReport,
)
from migration.domain.interfaces import (
    ConnectionFactory,
    DataExtractor,
    DataLoader,
    DataTransformer,
    DBConnection,
    SchemaAnalyzer,
)
from migration.infrastructure.reporter import SimpleMigrationReporter
from migration.infrastructure.rollback_manager import RollbackManager


class MigrationFacade:
    """SRP per subsystem, DIP at the boundary: every collaborator is injected."""

    def __init__(
        self,
        connection_factory: ConnectionFactory,
        schema_analyzer: SchemaAnalyzer,
        extractor: DataExtractor,
        transformer: DataTransformer,
        loader: DataLoader,
        reporter: SimpleMigrationReporter | None = None,
        rollback_manager: RollbackManager | None = None,
    ) -> None:
        self._connections = connection_factory
        self._schema_analyzer = schema_analyzer
        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader
        self._reporter = reporter or SimpleMigrationReporter()
        self._rollback_manager = rollback_manager or RollbackManager()

    def migrate(
        self,
        source: ConnectionConfig,
        dest: ConnectionConfig,
        tables: list[str],
        batch_size: int = 500,
    ) -> MigrationReport:
        migration_id = str(uuid4())
        started_at = datetime.now(UTC)

        source_conn = self._connections.connect(source)
        dest_conn = self._connections.connect(dest)
        table_results: list[TableMigrationResult] = []
        try:
            for table in tables:
                table_results.append(
                    self._migrate_one_table(
                        migration_id, source_conn, dest_conn, table, batch_size
                    )
                )
        finally:
            source_conn.close()
            dest_conn.close()

        finished_at = datetime.now(UTC)
        report = self._reporter.build_report(
            migration_id, table_results, started_at, finished_at
        )

        if not report.success:
            self.rollback(migration_id, dest)
        return report

    def _migrate_one_table(
        self,
        migration_id: str,
        source_conn: DBConnection,
        dest_conn: DBConnection,
        table: str,
        batch_size: int,
    ) -> TableMigrationResult:
        rows_extracted = 0
        rows_loaded = 0
        errors: list[str] = []
        try:
            schema = self._schema_analyzer.analyze(source_conn, table)
            for batch in self._extractor.extract_batches(
                source_conn, table, batch_size
            ):
                rows_extracted += len(batch)
                transformed = self._transformer.transform(batch, schema)
                rows_loaded += self._loader.load(dest_conn, table, transformed)
            self._rollback_manager.record(migration_id, table)
        except Exception as exc:  # noqa: BLE001 - reported per table, not raised
            errors.append(str(exc))
        return TableMigrationResult(table, rows_extracted, rows_loaded, errors)

    def dry_run(self, source: ConnectionConfig, tables: list[str]) -> ValidationReport:
        """Analyze the source schema without touching the destination."""
        issues: list[ValidationIssue] = []
        source_conn = self._connections.connect(source)
        try:
            for table in tables:
                try:
                    schema = self._schema_analyzer.analyze(source_conn, table)
                    if schema.row_count == 0:
                        issues.append(
                            ValidationIssue(table, "Table is empty", "warning")
                        )
                except Exception as exc:  # noqa: BLE001 - collected as an issue
                    issues.append(ValidationIssue(table, str(exc), "error"))
        finally:
            source_conn.close()
        return ValidationReport(tables_checked=tables, issues=issues)

    def rollback(self, migration_id: str, dest: ConnectionConfig) -> bool:
        dest_conn = self._connections.connect(dest)
        try:
            return self._rollback_manager.rollback(migration_id, dest_conn)
        finally:
            dest_conn.close()
