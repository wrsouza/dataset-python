"""End-to-end integration tests — real sqlite connections stand in for MySQL/PostgreSQL.

DriverConnectionFactory, GenericSchemaAnalyzer, BatchDataExtractor,
TrimmingTypeTransformer and GenericDataLoader all run for real here; only the
network database servers are swapped for sqlite, since the Facade's contract
(DB-API cursor.description/fetchmany/executemany) is identical across drivers.
"""

from __future__ import annotations

import sqlite3

from migration.application.facade import MigrationFacade
from migration.domain.entities import ConnectionConfig


def test_full_migration_copies_rows_and_trims_whitespace(
    facade: MigrationFacade,
    source_config: ConnectionConfig,
    dest_config: ConnectionConfig,
    dest_connection: sqlite3.Connection,
) -> None:
    report = facade.migrate(source_config, dest_config, tables=["orders"])

    assert report.success is True
    assert report.tables[0].rows_loaded == 3

    rows = dest_connection.execute("SELECT customer FROM orders ORDER BY id").fetchall()
    assert rows[0][0] == "Alice"  # whitespace was trimmed by the transformer


def test_migration_with_small_batch_size_still_copies_all_rows(
    facade: MigrationFacade,
    source_config: ConnectionConfig,
    dest_config: ConnectionConfig,
    dest_connection: sqlite3.Connection,
) -> None:
    report = facade.migrate(source_config, dest_config, tables=["orders"], batch_size=1)

    assert report.tables[0].rows_extracted == 3
    assert report.tables[0].rows_loaded == 3
    count = dest_connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert count == 3


def test_migration_of_unknown_table_triggers_rollback(
    facade: MigrationFacade,
    source_config: ConnectionConfig,
    dest_config: ConnectionConfig,
) -> None:
    report = facade.migrate(source_config, dest_config, tables=["does_not_exist"])

    assert report.success is False
    assert report.tables[0].errors


def test_dry_run_reports_empty_table_warning(
    facade: MigrationFacade, source_config: ConnectionConfig
) -> None:
    report = facade.dry_run(source_config, tables=["empty_table"])

    assert report.is_valid is True
    assert report.issues[0].table_name == "empty_table"
    assert report.issues[0].severity == "warning"


def test_partial_failure_rolls_back_successful_table_too(
    facade: MigrationFacade,
    source_config: ConnectionConfig,
    dest_config: ConnectionConfig,
    dest_connection: sqlite3.Connection,
) -> None:
    """One bad table in the batch rolls back every table touched by that migration."""
    report = facade.migrate(
        source_config, dest_config, tables=["orders", "does_not_exist"]
    )

    assert report.success is False
    count = dest_connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert count == 0  # rolled back even though "orders" itself succeeded
