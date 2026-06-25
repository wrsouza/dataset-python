"""Unit tests for MigrationFacade — all 4 subsystems mocked (DIP in action)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

from migration.application.facade import MigrationFacade
from migration.domain.entities import (
    ColumnInfo,
    ConnectionConfig,
    TableSchema,
)


def _make_facade_with_mocks() -> tuple[MigrationFacade, dict[str, MagicMock]]:
    mocks = {
        "connection_factory": MagicMock(),
        "schema_analyzer": MagicMock(),
        "extractor": MagicMock(),
        "transformer": MagicMock(),
        "loader": MagicMock(),
    }
    facade = MigrationFacade(
        connection_factory=mocks["connection_factory"],
        schema_analyzer=mocks["schema_analyzer"],
        extractor=mocks["extractor"],
        transformer=mocks["transformer"],
        loader=mocks["loader"],
    )
    return facade, mocks


def test_migrate_happy_path_reports_success() -> None:
    facade, mocks = _make_facade_with_mocks()
    schema = TableSchema("orders", [ColumnInfo("id", "INTEGER")], row_count=2)
    mocks["schema_analyzer"].analyze.return_value = schema
    mocks["extractor"].extract_batches.return_value = iter([[{"id": 1}], [{"id": 2}]])
    mocks["transformer"].transform.side_effect = lambda rows, _schema: rows
    mocks["loader"].load.side_effect = lambda _conn, _table, rows: len(rows)

    report = facade.migrate(
        ConnectionConfig("mysql", "mysql://x"),
        ConnectionConfig("postgresql", "postgresql://y"),
        tables=["orders"],
    )

    assert report.success is True
    assert report.total_rows_loaded == 2
    assert report.tables[0].rows_extracted == 2


def test_migrate_closes_connections_even_on_failure() -> None:
    facade, mocks = _make_facade_with_mocks()
    source_conn, dest_conn, rollback_conn = MagicMock(), MagicMock(), MagicMock()
    # 3 connects: migrate() opens source+dest, then rollback() opens dest again.
    mocks["connection_factory"].connect.side_effect = [
        source_conn,
        dest_conn,
        rollback_conn,
    ]
    mocks["schema_analyzer"].analyze.side_effect = RuntimeError("boom")

    facade.migrate(
        ConnectionConfig("mysql", "mysql://x"),
        ConnectionConfig("postgresql", "postgresql://y"),
        tables=["orders"],
    )

    source_conn.close.assert_called_once()
    dest_conn.close.assert_called_once()
    rollback_conn.close.assert_called_once()


def test_migrate_records_table_error_without_raising() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["schema_analyzer"].analyze.side_effect = RuntimeError("table missing")

    report = facade.migrate(
        ConnectionConfig("mysql", "mysql://x"),
        ConnectionConfig("postgresql", "postgresql://y"),
        tables=["missing_table"],
    )

    assert report.success is False
    assert "table missing" in report.tables[0].errors[0]


def test_migrate_rolls_back_destination_on_table_failure() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["schema_analyzer"].analyze.side_effect = RuntimeError("boom")

    facade.migrate(
        ConnectionConfig("mysql", "mysql://x"),
        ConnectionConfig("postgresql", "postgresql://y"),
        tables=["orders"],
    )

    # rollback() opens its own destination connection via the factory
    assert mocks["connection_factory"].connect.call_count >= 3


def test_dry_run_flags_empty_table_as_warning() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["schema_analyzer"].analyze.return_value = TableSchema(
        "empty_table", [], row_count=0
    )

    report = facade.dry_run(
        ConnectionConfig("mysql", "mysql://x"), tables=["empty_table"]
    )

    assert report.is_valid is True  # warnings don't invalidate the report
    assert report.issues[0].severity == "warning"


def test_dry_run_flags_analyzer_error_as_error_severity() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["schema_analyzer"].analyze.side_effect = RuntimeError("no such table")

    report = facade.dry_run(ConnectionConfig("mysql", "mysql://x"), tables=["ghost"])

    assert report.is_valid is False
    assert report.issues[0].severity == "error"


def test_rollback_delegates_to_rollback_manager() -> None:
    facade, mocks = _make_facade_with_mocks()
    rollback_manager = MagicMock()
    rollback_manager.rollback.return_value = True
    facade = MigrationFacade(
        connection_factory=mocks["connection_factory"],
        schema_analyzer=mocks["schema_analyzer"],
        extractor=mocks["extractor"],
        transformer=mocks["transformer"],
        loader=mocks["loader"],
        rollback_manager=rollback_manager,
    )

    result = facade.rollback("mig-1", ConnectionConfig("postgresql", "postgresql://y"))

    assert result is True
    rollback_manager.rollback.assert_called_once()


def test_migration_report_duration_is_non_negative() -> None:
    facade, mocks = _make_facade_with_mocks()
    mocks["schema_analyzer"].analyze.return_value = TableSchema(
        "t", [ColumnInfo("id", "INTEGER")], row_count=0
    )
    mocks["extractor"].extract_batches.return_value = iter([])

    report = facade.migrate(
        ConnectionConfig("mysql", "mysql://x"),
        ConnectionConfig("postgresql", "postgresql://y"),
        tables=["t"],
    )

    assert report.duration_seconds >= 0
    assert report.finished_at >= report.started_at
    assert isinstance(report.started_at, datetime)
    assert report.started_at.tzinfo == UTC
