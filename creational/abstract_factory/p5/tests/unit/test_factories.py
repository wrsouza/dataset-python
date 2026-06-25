"""Unit tests for the concrete factories, products and the factory registry.

No real database connections are made: ping()/execute() catch connection
errors internally (by design — see docstrings in factories.py), so these
tests exercise the Abstract Factory structure without requiring Docker.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from db_factory.domain.entities import QueryExecutionError
from db_factory.domain.interfaces import (
    DatabaseFactory,
    DBConnection,
    MigrationRunner,
    QueryBuilder,
)
from db_factory.infrastructure.factories import (
    DB_FACTORIES,
    MySQLConnection,
    MySQLFactory,
    MySQLMigrationRunner,
    MySQLQueryBuilder,
    PostgreSQLConnection,
    PostgreSQLFactory,
    PostgreSQLMigrationRunner,
    PostgreSQLQueryBuilder,
    SQLServerConnection,
    SQLServerFactory,
    SQLServerMigrationRunner,
    SQLServerQueryBuilder,
    get_factory_for_engine,
)


class TestPostgreSQLFamily:
    """ConcreteFactory: PostgreSQLFactory produces a consistent product family."""

    def test_get_engine_name(self) -> None:
        assert PostgreSQLFactory().get_engine_name() == "PostgreSQL"

    def test_create_connection_returns_postgres_connection(self) -> None:
        connection = PostgreSQLFactory().create_connection()
        assert isinstance(connection, PostgreSQLConnection)
        assert isinstance(connection, DBConnection)
        assert connection.get_engine_name() == "PostgreSQL"

    def test_create_query_builder_returns_postgres_builder(self) -> None:
        builder = PostgreSQLFactory().create_query_builder()
        assert isinstance(builder, PostgreSQLQueryBuilder)
        assert isinstance(builder, QueryBuilder)
        assert builder.get_engine_name() == "PostgreSQL"

    def test_create_migration_runner_returns_postgres_runner(self) -> None:
        runner = PostgreSQLFactory().create_migration_runner()
        assert isinstance(runner, PostgreSQLMigrationRunner)
        assert isinstance(runner, MigrationRunner)
        assert runner.get_engine_name() == "PostgreSQL"

    def test_select_builds_correct_sql(self) -> None:
        builder = PostgreSQLQueryBuilder()
        sql = builder.select("users", ["id", "name"])
        assert sql == "SELECT id, name FROM users;"

    def test_select_without_columns_uses_wildcard(self) -> None:
        builder = PostgreSQLQueryBuilder()
        assert builder.select("users", []) == "SELECT * FROM users;"

    def test_ping_returns_false_when_unreachable(self) -> None:
        # No real postgres available in unit tests -> connection must fail closed.
        connection = PostgreSQLConnection()
        assert connection.ping() is False

    def test_get_connection_info_never_leaks_password(self) -> None:
        connection = PostgreSQLConnection()
        info = connection.get_connection_info()
        assert "secret" not in info.get("host_db", "")

    def test_execute_raises_query_execution_error_when_unreachable(self) -> None:
        builder = PostgreSQLQueryBuilder()
        with pytest.raises(QueryExecutionError) as exc_info:
            builder.execute("SELECT 1;")
        assert exc_info.value.engine == "PostgreSQL"

    def test_run_pending_returns_applied_migration_labels(self) -> None:
        def fake_call_command(*_args: object, **kwargs: object) -> None:
            kwargs["stdout"].write("Applying app.0002_add_index... OK\n")  # type: ignore[union-attr]

        with patch(
            "django.core.management.call_command", side_effect=fake_call_command
        ):
            applied = PostgreSQLMigrationRunner().run_pending()
        assert applied == ["Applying app.0002_add_index... OK"]

    def test_list_applied_returns_formatted_labels(self) -> None:
        executor = MagicMock()
        executor.loader.applied_migrations = {("app", "0001_initial")}
        with patch(
            "django.db.migrations.executor.MigrationExecutor", return_value=executor
        ):
            applied = PostgreSQLMigrationRunner().list_applied()
        assert applied == ["app.0001_initial"]

    def test_ping_returns_true_when_driver_connects(self) -> None:
        fake_psycopg2 = MagicMock()
        fake_psycopg2.connect.return_value = MagicMock()
        with patch.dict("sys.modules", {"psycopg2": fake_psycopg2}):
            assert PostgreSQLConnection().ping() is True


class TestMySQLFamily:
    """ConcreteFactory: MySQLFactory produces a consistent product family."""

    def test_get_engine_name(self) -> None:
        assert MySQLFactory().get_engine_name() == "MySQL"

    def test_create_connection_returns_mysql_connection(self) -> None:
        connection = MySQLFactory().create_connection()
        assert isinstance(connection, MySQLConnection)
        assert connection.get_engine_name() == "MySQL"

    def test_create_query_builder_returns_mysql_builder(self) -> None:
        builder = MySQLFactory().create_query_builder()
        assert isinstance(builder, MySQLQueryBuilder)
        assert builder.get_engine_name() == "MySQL"

    def test_create_migration_runner_returns_mysql_runner(self) -> None:
        runner = MySQLFactory().create_migration_runner()
        assert isinstance(runner, MySQLMigrationRunner)
        assert runner.get_engine_name() == "MySQL"

    def test_select_uses_backtick_quoting(self) -> None:
        builder = MySQLQueryBuilder()
        sql = builder.select("orders", ["id"])
        assert sql == "SELECT `id` FROM `orders`;"

    def test_ping_returns_false_when_unreachable(self) -> None:
        connection = MySQLConnection()
        assert connection.ping() is False

    def test_execute_raises_query_execution_error_when_unreachable(self) -> None:
        builder = MySQLQueryBuilder()
        with pytest.raises(QueryExecutionError) as exc_info:
            builder.execute("SELECT 1;")
        assert exc_info.value.engine == "MySQL"

    def test_run_pending_returns_applied_migration_labels(self) -> None:
        def fake_call_command(*_args: object, **kwargs: object) -> None:
            kwargs["stdout"].write("Applying app.0003_seed_data... OK\n")  # type: ignore[union-attr]

        with patch(
            "django.core.management.call_command", side_effect=fake_call_command
        ):
            applied = MySQLMigrationRunner().run_pending()
        assert applied == ["Applying app.0003_seed_data... OK"]

    def test_list_applied_returns_formatted_labels(self) -> None:
        executor = MagicMock()
        executor.loader.applied_migrations = {("app", "0001_initial")}
        sqlite_alias = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        with (
            patch(
                "django.db.migrations.executor.MigrationExecutor", return_value=executor
            ),
            patch.dict("django.db.connections.databases", {"mysql": sqlite_alias}),
        ):
            applied = MySQLMigrationRunner().list_applied()
        assert applied == ["app.0001_initial"]

    def test_ping_returns_true_when_driver_connects(self) -> None:
        fake_module = MagicMock()
        fake_module.connector.connect.return_value = MagicMock()
        with patch.dict(
            "sys.modules",
            {"mysql.connector": fake_module.connector, "mysql": fake_module},
        ):
            assert MySQLConnection().ping() is True

    def test_execute_returns_rows_when_driver_connects(self) -> None:
        fake_module = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.fetchall.return_value = [{"id": 1}]
        fake_module.connector.connect.return_value.cursor.return_value = fake_cursor
        with patch.dict(
            "sys.modules",
            {"mysql.connector": fake_module.connector, "mysql": fake_module},
        ):
            rows = MySQLQueryBuilder().execute("SELECT 1;")
        assert rows == [{"id": 1}]


class TestSQLServerFamily:
    """ConcreteFactory: SQLServerFactory produces a consistent product family."""

    def test_get_engine_name(self) -> None:
        assert SQLServerFactory().get_engine_name() == "SQLServer"

    def test_create_connection_returns_sqlserver_connection(self) -> None:
        connection = SQLServerFactory().create_connection()
        assert isinstance(connection, SQLServerConnection)
        assert connection.get_engine_name() == "SQLServer"

    def test_create_query_builder_returns_sqlserver_builder(self) -> None:
        builder = SQLServerFactory().create_query_builder()
        assert isinstance(builder, SQLServerQueryBuilder)
        assert builder.get_engine_name() == "SQLServer"

    def test_create_migration_runner_returns_sqlserver_runner(self) -> None:
        runner = SQLServerFactory().create_migration_runner()
        assert isinstance(runner, SQLServerMigrationRunner)
        assert runner.get_engine_name() == "SQLServer"

    def test_select_uses_bracket_quoting(self) -> None:
        builder = SQLServerQueryBuilder()
        sql = builder.select("orders", ["id"])
        assert sql == "SELECT [id] FROM [orders];"

    def test_ping_returns_false_when_unreachable(self) -> None:
        connection = SQLServerConnection()
        assert connection.ping() is False

    def test_execute_raises_query_execution_error_when_unreachable(self) -> None:
        builder = SQLServerQueryBuilder()
        with pytest.raises(QueryExecutionError) as exc_info:
            builder.execute("SELECT 1;")
        assert exc_info.value.engine == "SQLServer"

    def test_run_pending_returns_applied_migration_labels(self) -> None:
        def fake_call_command(*_args: object, **kwargs: object) -> None:
            kwargs["stdout"].write("Applying app.0004_views... OK\n")  # type: ignore[union-attr]

        with patch(
            "django.core.management.call_command", side_effect=fake_call_command
        ):
            applied = SQLServerMigrationRunner().run_pending()
        assert applied == ["Applying app.0004_views... OK"]

    def test_list_applied_returns_formatted_labels(self) -> None:
        executor = MagicMock()
        executor.loader.applied_migrations = {("app", "0001_initial")}
        sqlite_alias = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        with (
            patch(
                "django.db.migrations.executor.MigrationExecutor", return_value=executor
            ),
            patch.dict("django.db.connections.databases", {"sqlserver": sqlite_alias}),
        ):
            applied = SQLServerMigrationRunner().list_applied()
        assert applied == ["app.0001_initial"]

    def test_ping_returns_true_when_driver_connects(self) -> None:
        fake_pyodbc = MagicMock()
        fake_pyodbc.connect.return_value = MagicMock()
        with patch.dict("sys.modules", {"pyodbc": fake_pyodbc}):
            assert SQLServerConnection().ping() is True

    def test_execute_with_params_passes_values_as_list(self) -> None:
        fake_pyodbc = MagicMock()
        fake_cursor = MagicMock()
        fake_cursor.description = [("id",)]
        fake_cursor.fetchall.return_value = [(1,)]
        fake_pyodbc.connect.return_value.cursor.return_value = fake_cursor
        with patch.dict("sys.modules", {"pyodbc": fake_pyodbc}):
            rows = SQLServerQueryBuilder().execute("SELECT ?;", {"a": 1})
        assert rows == [{"id": 1}]
        fake_cursor.execute.assert_called_once_with("SELECT ?;", [1])


class TestFactoryRegistry:
    """OCP: new engines are registered in DB_FACTORIES — no if/elif chains."""

    def test_db_factories_contains_all_three_engines(self) -> None:
        assert set(DB_FACTORIES.keys()) == {"postgresql", "mysql", "sqlserver"}

    @pytest.mark.parametrize(
        ("db_type", "expected_engine"),
        [
            ("postgresql", "PostgreSQL"),
            ("POSTGRESQL", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("sqlserver", "SQLServer"),
        ],
    )
    def test_get_factory_for_engine_is_case_insensitive(
        self, db_type: str, expected_engine: str
    ) -> None:
        factory = get_factory_for_engine(db_type)
        assert isinstance(factory, DatabaseFactory)
        assert factory.get_engine_name() == expected_engine

    def test_unsupported_engine_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unsupported database type"):
            get_factory_for_engine("oracle")

    def test_value_error_lists_supported_engines(self) -> None:
        with pytest.raises(ValueError, match="postgresql"):
            get_factory_for_engine("mongodb")

    def test_each_factory_produces_independent_families(self) -> None:
        """OCP/LSP: every family's products report their own, distinct engine name."""
        engine_names = {
            get_factory_for_engine(db_type).create_connection().get_engine_name()
            for db_type in DB_FACTORIES
        }
        assert engine_names == {"PostgreSQL", "MySQL", "SQLServer"}
