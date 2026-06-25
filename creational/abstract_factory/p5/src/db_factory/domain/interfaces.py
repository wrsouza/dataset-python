"""Abstract interfaces for the Database Connector Factory pattern.

Defines the AbstractFactory and three AbstractProduct interfaces:
DBConnection, QueryBuilder, and MigrationRunner.

ISP: each product has its own small interface — clients that only need
     QueryBuilder do not depend on MigrationRunner or DBConnection.
OCP: add a new database engine by subclassing DatabaseFactory — zero edits
     to existing factories, use cases or Django views.
DIP: Django views depend on DatabaseFactory (abstraction), never on concrete classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

# ── AbstractProducts ───────────────────────────────────────────────────────────


class DBConnection(ABC):
    """AbstractProduct: represents an open (or lazy) database connection.

    ISP: connection management is its own interface, separate from query building
    and migration running. Clients that only check health use only this contract.
    """

    @abstractmethod
    def ping(self) -> bool:
        """Return True if the database is reachable, False otherwise.

        Implementations must never raise — they return False on failure so that
        health-check views can respond gracefully without 500 errors.
        """
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the human-readable engine name (e.g. 'PostgreSQL')."""
        ...

    @abstractmethod
    def get_connection_info(self) -> dict[str, str]:
        """Return a safe, redacted snapshot of connection parameters.

        Passwords must be masked — this dict may appear in API responses.
        """
        ...


class QueryBuilder(ABC):
    """AbstractProduct: constructs and executes safe parameterised queries.

    ISP: query execution is its own interface — health checks never need this.
    """

    @abstractmethod
    def select(self, table: str, columns: list[str]) -> str:
        """Return a SELECT statement for the given table and columns."""
        ...

    @abstractmethod
    def execute(
        self, sql: str, params: dict[str, object] | None = None
    ) -> list[dict[str, object]]:
        """Execute a query and return rows as a list of dicts.

        Raises QueryExecutionError on failure — never returns partial results.
        """
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the engine name for logging and telemetry."""
        ...


class MigrationRunner(ABC):
    """AbstractProduct: applies schema migrations for a specific engine.

    ISP: migration execution is its own interface — query clients never use it.
    """

    @abstractmethod
    def run_pending(self) -> list[str]:
        """Apply all pending migrations and return their names."""
        ...

    @abstractmethod
    def list_applied(self) -> list[str]:
        """Return the names of all already-applied migrations."""
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the engine name for logging and telemetry."""
        ...


# ── AbstractFactory ────────────────────────────────────────────────────────────


class DatabaseFactory(ABC):
    """AbstractFactory: creates a family of database interaction objects.

    Each ConcreteFactory produces objects that work together for a specific
    database engine (PostgreSQL, MySQL, SQL Server).

    OCP: add a new engine by subclassing DatabaseFactory — no existing code changes.
    DIP: Django views receive a DatabaseFactory and never import concrete classes.
    """

    @abstractmethod
    def create_connection(self) -> DBConnection:
        """Create and return an engine-specific DBConnection."""
        ...

    @abstractmethod
    def create_query_builder(self) -> QueryBuilder:
        """Create and return an engine-specific QueryBuilder."""
        ...

    @abstractmethod
    def create_migration_runner(self) -> MigrationRunner:
        """Create and return an engine-specific MigrationRunner."""
        ...

    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the human-readable name of the database engine."""
        ...
