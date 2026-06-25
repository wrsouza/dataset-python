"""Concrete Factories, Connections, QueryBuilders, and MigrationRunners.

Three engine families: PostgreSQL, MySQL, SQL Server.
Each family's objects are self-consistent and engine-specific.

OCP: adding SQLite / MongoDB / Oracle means subclassing DatabaseFactory
     and adding the new concrete products — zero changes to existing classes.
"""

from __future__ import annotations

import os
from typing import Any, cast

from db_factory.domain.entities import QueryExecutionError
from db_factory.domain.interfaces import (
    DBConnection,
    DatabaseFactory,
    MigrationRunner,
    QueryBuilder,
)

# ── PostgreSQL Family ──────────────────────────────────────────────────────────


class PostgreSQLConnection(DBConnection):
    """ConcreteProduct: DBConnection backed by psycopg2."""

    def __init__(self) -> None:
        self._dsn = os.getenv(
            "POSTGRES_DSN",
            "postgresql://app:secret@postgres:5432/appdb",
        )

    def ping(self) -> bool:
        try:
            import psycopg2

            conn = psycopg2.connect(self._dsn, connect_timeout=3)
            conn.close()
            return True
        except Exception:  # noqa: BLE001
            return False

    def get_engine_name(self) -> str:
        return "PostgreSQL"

    def get_connection_info(self) -> dict[str, str]:
        # DSN may contain credentials — return only host/db info.
        parts = self._dsn.split("@")
        host_db = parts[-1] if len(parts) > 1 else self._dsn
        return {"engine": "PostgreSQL", "host_db": host_db, "driver": "psycopg2"}


class PostgreSQLQueryBuilder(QueryBuilder):
    """ConcreteProduct: parameterised query builder for PostgreSQL."""

    def __init__(self) -> None:
        self._dsn = os.getenv(
            "POSTGRES_DSN",
            "postgresql://app:secret@postgres:5432/appdb",
        )

    def select(self, table: str, columns: list[str]) -> str:
        cols = ", ".join(columns) if columns else "*"
        return f"SELECT {cols} FROM {table};"

    def execute(
        self, sql: str, params: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            with psycopg2.connect(self._dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(sql, params)
                    rows: list[dict[str, Any]] = [dict(r) for r in cur.fetchall()]
            return rows
        except Exception as exc:
            raise QueryExecutionError("PostgreSQL", sql, str(exc)) from exc

    def get_engine_name(self) -> str:
        return "PostgreSQL"


class PostgreSQLMigrationRunner(MigrationRunner):
    """ConcreteProduct: Django-managed migrations for PostgreSQL.

    Uses Django's built-in migration framework. The concrete runner
    wraps Django management commands so the use case stays framework-agnostic.
    """

    def run_pending(self) -> list[str]:
        """Apply all pending Django migrations and return their labels."""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command("migrate", "--no-input", stdout=out, verbosity=1)
        return [
            line.strip() for line in out.getvalue().splitlines() if "Applying" in line
        ]

    def list_applied(self) -> list[str]:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections

        executor = MigrationExecutor(connections["default"])
        applied = executor.loader.applied_migrations
        return [f"{app}.{name}" for app, name in applied]

    def get_engine_name(self) -> str:
        return "PostgreSQL"


# ── MySQL Family ───────────────────────────────────────────────────────────────


class MySQLConnection(DBConnection):
    """ConcreteProduct: DBConnection backed by mysql-connector-python."""

    def __init__(self) -> None:
        self._host = os.getenv("MYSQL_HOST", "mysql")
        self._port = int(os.getenv("MYSQL_PORT", "3306"))
        self._user = os.getenv("MYSQL_USER", "app")
        self._password = os.getenv("MYSQL_PASSWORD", "secret")
        self._database = os.getenv("MYSQL_DATABASE", "appdb")

    def ping(self) -> bool:
        try:
            import mysql.connector

            conn = mysql.connector.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                connection_timeout=3,
            )
            conn.close()
            return True
        except Exception:  # noqa: BLE001
            return False

    def get_engine_name(self) -> str:
        return "MySQL"

    def get_connection_info(self) -> dict[str, str]:
        return {
            "engine": "MySQL",
            "host": self._host,
            "port": str(self._port),
            "database": self._database,
            "driver": "mysql-connector-python",
        }


class MySQLQueryBuilder(QueryBuilder):
    """ConcreteProduct: parameterised query builder for MySQL."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "host": os.getenv("MYSQL_HOST", "mysql"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": os.getenv("MYSQL_USER", "app"),
            "password": os.getenv("MYSQL_PASSWORD", "secret"),
            "database": os.getenv("MYSQL_DATABASE", "appdb"),
        }

    def select(self, table: str, columns: list[str]) -> str:
        cols = ", ".join(f"`{c}`" for c in columns) if columns else "*"
        return f"SELECT {cols} FROM `{table}`;"

    def execute(
        self, sql: str, params: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        try:
            import mysql.connector

            conn = mysql.connector.connect(**self._config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, cast(Any, params or {}))
            rows: list[dict[str, Any]] = cast(
                list[dict[str, Any]], list(cursor.fetchall())
            )
            cursor.close()
            conn.close()
            return rows
        except Exception as exc:
            raise QueryExecutionError("MySQL", sql, str(exc)) from exc

    def get_engine_name(self) -> str:
        return "MySQL"


class MySQLMigrationRunner(MigrationRunner):
    """ConcreteProduct: Django-managed migrations for MySQL.

    Implementation mirrors PostgreSQLMigrationRunner — both use Django's
    migration framework. The engine-specific concern is only the connection.
    """

    def run_pending(self) -> list[str]:
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command(
            "migrate", "--no-input", "--database=mysql", stdout=out, verbosity=1
        )
        return [
            line.strip() for line in out.getvalue().splitlines() if "Applying" in line
        ]

    def list_applied(self) -> list[str]:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections

        executor = MigrationExecutor(connections["mysql"])
        applied = executor.loader.applied_migrations
        return [f"{app}.{name}" for app, name in applied]

    def get_engine_name(self) -> str:
        return "MySQL"


# ── SQL Server Family ──────────────────────────────────────────────────────────


class SQLServerConnection(DBConnection):
    """ConcreteProduct: DBConnection backed by pyodbc / mssql."""

    def __init__(self) -> None:
        self._host = os.getenv("SQLSERVER_HOST", "sqlserver")
        self._port = os.getenv("SQLSERVER_PORT", "1433")
        self._user = os.getenv("SQLSERVER_USER", "sa")
        self._password = os.getenv("SQLSERVER_PASSWORD", "YourStrong@Passw0rd")
        self._database = os.getenv("SQLSERVER_DATABASE", "appdb")

    def _build_connection_string(self) -> str:
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self._host},{self._port};"
            f"DATABASE={self._database};"
            f"UID={self._user};"
            f"PWD={self._password};"
            "TrustServerCertificate=yes;"
        )

    def ping(self) -> bool:
        try:
            import pyodbc

            conn = pyodbc.connect(self._build_connection_string(), timeout=3)
            conn.close()
            return True
        except Exception:  # noqa: BLE001
            return False

    def get_engine_name(self) -> str:
        return "SQLServer"

    def get_connection_info(self) -> dict[str, str]:
        return {
            "engine": "SQL Server",
            "host": self._host,
            "port": self._port,
            "database": self._database,
            "driver": "pyodbc / ODBC Driver 18",
        }


class SQLServerQueryBuilder(QueryBuilder):
    """ConcreteProduct: parameterised query builder for SQL Server.

    Uses T-SQL syntax. Parameterised queries use ? placeholders (pyodbc style).
    """

    def __init__(self) -> None:
        self._host = os.getenv("SQLSERVER_HOST", "sqlserver")
        self._port = os.getenv("SQLSERVER_PORT", "1433")
        self._user = os.getenv("SQLSERVER_USER", "sa")
        self._password = os.getenv("SQLSERVER_PASSWORD", "YourStrong@Passw0rd")
        self._database = os.getenv("SQLSERVER_DATABASE", "appdb")

    def _build_connection_string(self) -> str:
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self._host},{self._port};"
            f"DATABASE={self._database};"
            f"UID={self._user};"
            f"PWD={self._password};"
            "TrustServerCertificate=yes;"
        )

    def select(self, table: str, columns: list[str]) -> str:
        cols = ", ".join(f"[{c}]" for c in columns) if columns else "*"
        return f"SELECT {cols} FROM [{table}];"

    def execute(
        self, sql: str, params: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        try:
            import pyodbc

            conn = pyodbc.connect(self._build_connection_string())
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, list(params.values()))
            else:
                cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description or []]
            rows: list[dict[str, Any]] = [
                dict(zip(columns, row, strict=False)) for row in cursor.fetchall()
            ]
            conn.close()
            return rows
        except Exception as exc:
            raise QueryExecutionError("SQLServer", sql, str(exc)) from exc

    def get_engine_name(self) -> str:
        return "SQLServer"


class SQLServerMigrationRunner(MigrationRunner):
    """ConcreteProduct: Django-managed migrations for SQL Server."""

    def run_pending(self) -> list[str]:
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command(
            "migrate", "--no-input", "--database=sqlserver", stdout=out, verbosity=1
        )
        return [
            line.strip() for line in out.getvalue().splitlines() if "Applying" in line
        ]

    def list_applied(self) -> list[str]:
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connections

        executor = MigrationExecutor(connections["sqlserver"])
        applied = executor.loader.applied_migrations
        return [f"{app}.{name}" for app, name in applied]

    def get_engine_name(self) -> str:
        return "SQLServer"


# ── Concrete Factories ─────────────────────────────────────────────────────────


class PostgreSQLFactory(DatabaseFactory):
    """ConcreteFactory: creates the PostgreSQL product family."""

    def create_connection(self) -> PostgreSQLConnection:
        return PostgreSQLConnection()

    def create_query_builder(self) -> PostgreSQLQueryBuilder:
        return PostgreSQLQueryBuilder()

    def create_migration_runner(self) -> PostgreSQLMigrationRunner:
        return PostgreSQLMigrationRunner()

    def get_engine_name(self) -> str:
        return "PostgreSQL"


class MySQLFactory(DatabaseFactory):
    """ConcreteFactory: creates the MySQL product family."""

    def create_connection(self) -> MySQLConnection:
        return MySQLConnection()

    def create_query_builder(self) -> MySQLQueryBuilder:
        return MySQLQueryBuilder()

    def create_migration_runner(self) -> MySQLMigrationRunner:
        return MySQLMigrationRunner()

    def get_engine_name(self) -> str:
        return "MySQL"


class SQLServerFactory(DatabaseFactory):
    """ConcreteFactory: creates the SQL Server product family."""

    def create_connection(self) -> SQLServerConnection:
        return SQLServerConnection()

    def create_query_builder(self) -> SQLServerQueryBuilder:
        return SQLServerQueryBuilder()

    def create_migration_runner(self) -> SQLServerMigrationRunner:
        return SQLServerMigrationRunner()

    def get_engine_name(self) -> str:
        return "SQLServer"


# ── Factory Registry ───────────────────────────────────────────────────────────

DB_FACTORIES: dict[str, DatabaseFactory] = {
    "postgresql": PostgreSQLFactory(),
    "mysql": MySQLFactory(),
    "sqlserver": SQLServerFactory(),
}


def get_factory_for_engine(db_type: str) -> DatabaseFactory:
    """Return the appropriate DatabaseFactory for the given engine identifier.

    OCP: registering a new engine only requires an entry in DB_FACTORIES.
    No if/elif chains are scattered across views or use cases.
    """
    factory = DB_FACTORIES.get(db_type.lower())
    if factory is None:
        supported = ", ".join(DB_FACTORIES.keys())
        raise ValueError(
            f"Unsupported database type '{db_type}'. Supported: {supported}"
        )
    return factory
