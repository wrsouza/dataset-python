"""Application use cases for the Database Connector Factory.

The Client role in the Abstract Factory pattern lives here.
All use cases depend on DatabaseFactory (abstraction) — never on concrete classes.
This enforces the Dependency Inversion Principle throughout the application layer.
"""

from __future__ import annotations

from db_factory.domain.entities import HealthCheckResult, MigrationReport, QueryResult
from db_factory.domain.interfaces import DatabaseFactory


class CheckDatabaseHealthUseCase:
    """Client: checks whether a database engine is reachable.

    DIP: receives DatabaseFactory via constructor.
    SRP: single responsibility — health check only, no query execution.
    """

    def __init__(self, factory: DatabaseFactory) -> None:
        self._factory = factory

    def execute(self) -> HealthCheckResult:
        """Ping the database and return a HealthCheckResult.

        Never raises — failure is represented as is_healthy=False with
        an error_message, so HTTP views always return a structured response.
        """
        connection = self._factory.create_connection()
        engine = self._factory.get_engine_name()
        try:
            is_healthy = connection.ping()
            info = connection.get_connection_info()
            return HealthCheckResult(
                engine=engine,
                is_healthy=is_healthy,
                connection_info=info,
            )
        except Exception as exc:  # noqa: BLE001
            # Broad catch is intentional: health check must not propagate
            # engine-specific exceptions to the HTTP layer.
            return HealthCheckResult(
                engine=engine,
                is_healthy=False,
                error_message=str(exc),
            )


class ExecuteQueryUseCase:
    """Client: executes a parameterised query via the factory's QueryBuilder.

    DIP: depends on DatabaseFactory, not on psycopg2 / mysql-connector / pyodbc.
    SRP: query execution only — no health check, no migration logic.
    """

    def __init__(self, factory: DatabaseFactory) -> None:
        self._factory = factory

    def execute(
        self,
        sql: str,
        params: dict[str, object] | None = None,
    ) -> QueryResult:
        """Execute the given SQL and return a QueryResult.

        Raises QueryExecutionError (domain exception) on failure.
        """
        query_builder = self._factory.create_query_builder()
        rows = query_builder.execute(sql, params)
        return QueryResult(
            engine=self._factory.get_engine_name(),
            sql=sql,
            rows=rows,
            row_count=len(rows),
        )


class RunMigrationsUseCase:
    """Client: applies pending database migrations via the factory's MigrationRunner.

    DIP: depends on DatabaseFactory — the migration strategy is engine-specific
         but the use case is oblivious to the concrete implementation.
    SRP: migration orchestration only.
    """

    def __init__(self, factory: DatabaseFactory) -> None:
        self._factory = factory

    def execute(self) -> MigrationReport:
        """Run all pending migrations and return a MigrationReport."""
        runner = self._factory.create_migration_runner()
        pending_before = len(runner.list_applied())
        applied = runner.run_pending()
        return MigrationReport(
            engine=self._factory.get_engine_name(),
            applied=applied,
            pending_before=pending_before,
        )
