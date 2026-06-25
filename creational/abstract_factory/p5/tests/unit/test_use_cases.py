"""Unit tests for db_factory application use cases.

No real databases are required — all dependencies are mocked via
unittest.mock.MagicMock with `spec=` for interface compliance.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from db_factory.application.use_cases import (
    CheckDatabaseHealthUseCase,
    ExecuteQueryUseCase,
    RunMigrationsUseCase,
)
from db_factory.domain.entities import HealthCheckResult, MigrationReport, QueryResult
from db_factory.domain.interfaces import (
    DatabaseFactory,
    DBConnection,
    MigrationRunner,
    QueryBuilder,
)


@pytest.fixture
def mock_connection() -> MagicMock:
    return MagicMock(spec=DBConnection)


@pytest.fixture
def mock_query_builder() -> MagicMock:
    return MagicMock(spec=QueryBuilder)


@pytest.fixture
def mock_migration_runner() -> MagicMock:
    return MagicMock(spec=MigrationRunner)


@pytest.fixture
def mock_factory(
    mock_connection: MagicMock,
    mock_query_builder: MagicMock,
    mock_migration_runner: MagicMock,
) -> MagicMock:
    """A mock DatabaseFactory wired to produce the other mocked products."""
    factory = MagicMock(spec=DatabaseFactory)
    factory.create_connection.return_value = mock_connection
    factory.create_query_builder.return_value = mock_query_builder
    factory.create_migration_runner.return_value = mock_migration_runner
    factory.get_engine_name.return_value = "PostgreSQL"
    return factory


class TestCheckDatabaseHealthUseCase:
    """DIP: the use case only depends on DatabaseFactory, never on concrete classes."""

    def test_returns_healthy_result_when_ping_succeeds(
        self, mock_factory: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.ping.return_value = True
        mock_connection.get_connection_info.return_value = {"host_db": "db:5432/appdb"}

        result = CheckDatabaseHealthUseCase(mock_factory).execute()

        assert isinstance(result, HealthCheckResult)
        assert result.is_healthy is True
        assert result.engine == "PostgreSQL"
        assert result.connection_info == {"host_db": "db:5432/appdb"}
        assert result.error_message is None

    def test_returns_unhealthy_result_when_ping_fails(
        self, mock_factory: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.ping.return_value = False
        mock_connection.get_connection_info.return_value = {}

        result = CheckDatabaseHealthUseCase(mock_factory).execute()

        assert result.is_healthy is False
        assert result.error_message is None

    def test_never_raises_when_connection_throws(
        self, mock_factory: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.ping.side_effect = RuntimeError("network unreachable")

        result = CheckDatabaseHealthUseCase(mock_factory).execute()

        assert result.is_healthy is False
        assert result.error_message == "network unreachable"

    def test_delegates_connection_creation_to_factory(
        self, mock_factory: MagicMock, mock_connection: MagicMock
    ) -> None:
        mock_connection.ping.return_value = True
        mock_connection.get_connection_info.return_value = {}

        CheckDatabaseHealthUseCase(mock_factory).execute()

        mock_factory.create_connection.assert_called_once()


class TestExecuteQueryUseCase:
    """DIP: depends only on DatabaseFactory; SRP: query execution only."""

    def test_returns_query_result_with_rows(
        self, mock_factory: MagicMock, mock_query_builder: MagicMock
    ) -> None:
        mock_query_builder.execute.return_value = [{"id": 1}, {"id": 2}]

        result = ExecuteQueryUseCase(mock_factory).execute("SELECT * FROM t;")

        assert isinstance(result, QueryResult)
        assert result.row_count == 2
        assert result.rows == [{"id": 1}, {"id": 2}]
        assert result.engine == "PostgreSQL"

    def test_passes_sql_and_params_to_query_builder(
        self, mock_factory: MagicMock, mock_query_builder: MagicMock
    ) -> None:
        mock_query_builder.execute.return_value = []

        ExecuteQueryUseCase(mock_factory).execute("SELECT 1;", {"a": 1})

        mock_query_builder.execute.assert_called_once_with("SELECT 1;", {"a": 1})

    def test_propagates_query_execution_error(
        self, mock_factory: MagicMock, mock_query_builder: MagicMock
    ) -> None:
        from db_factory.domain.entities import QueryExecutionError

        mock_query_builder.execute.side_effect = QueryExecutionError(
            "PostgreSQL", "SELECT 1;", "syntax error"
        )

        with pytest.raises(QueryExecutionError):
            ExecuteQueryUseCase(mock_factory).execute("SELECT 1;")


class TestRunMigrationsUseCase:
    """SRP: migration orchestration only — no health check, no query logic."""

    def test_returns_migration_report(
        self, mock_factory: MagicMock, mock_migration_runner: MagicMock
    ) -> None:
        mock_migration_runner.list_applied.return_value = ["app.0001"]
        mock_migration_runner.run_pending.return_value = ["app.0002_add_index"]

        report = RunMigrationsUseCase(mock_factory).execute()

        assert isinstance(report, MigrationReport)
        assert report.engine == "PostgreSQL"
        assert report.applied == ["app.0002_add_index"]
        assert report.pending_before == 1

    def test_calls_list_applied_before_run_pending(
        self, mock_factory: MagicMock, mock_migration_runner: MagicMock
    ) -> None:
        mock_migration_runner.list_applied.return_value = []
        mock_migration_runner.run_pending.return_value = []

        RunMigrationsUseCase(mock_factory).execute()

        mock_migration_runner.list_applied.assert_called_once()
        mock_migration_runner.run_pending.assert_called_once()


class TestDependencyInversion:
    """DIP: use cases work identically regardless of which factory is injected."""

    @pytest.mark.parametrize("engine_name", ["PostgreSQL", "MySQL", "SQLServer"])
    def test_health_check_works_with_any_engine_name(self, engine_name: str) -> None:
        factory = MagicMock(spec=DatabaseFactory)
        connection = MagicMock(spec=DBConnection)
        connection.ping.return_value = True
        connection.get_connection_info.return_value = {}
        factory.create_connection.return_value = connection
        factory.get_engine_name.return_value = engine_name

        result = CheckDatabaseHealthUseCase(factory).execute()

        assert result.engine == engine_name
