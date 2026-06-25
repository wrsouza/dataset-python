"""ConnectionFactory: picks the right DB-API driver for a dialect."""

from __future__ import annotations

import sqlite3
from typing import Any
from urllib.parse import urlparse

from migration.domain.entities import ConnectionConfig
from migration.domain.interfaces import ConnectionFactory


class UnsupportedDialectError(ValueError):
    def __init__(self, dialect: str) -> None:
        super().__init__(f"Unsupported dialect: {dialect!r}")


class DriverConnectionFactory(ConnectionFactory):
    """Connects to sqlite (tests/local), MySQL, or PostgreSQL from one config."""

    def connect(self, config: ConnectionConfig) -> Any:
        if config.dialect == "sqlite":
            return sqlite3.connect(config.dsn)
        if config.dialect == "mysql":
            return self._connect_mysql(config.dsn)
        if config.dialect == "postgresql":
            return self._connect_postgresql(config.dsn)
        raise UnsupportedDialectError(config.dialect)

    def _connect_mysql(self, dsn: str) -> Any:
        import pymysql

        parsed = urlparse(dsn)
        return pymysql.connect(
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username or "root",
            password=parsed.password or "",
            database=parsed.path.lstrip("/"),
        )

    def _connect_postgresql(self, dsn: str) -> Any:
        import psycopg2

        return psycopg2.connect(dsn)
