"""ConnectionFactory: picks the right DB-API driver for a dialect.

`sqlite` is used as a MySQL stand-in in tests/local dev — both drivers
honor the same DB-API 2.0 cursor contract (`execute`/`fetchall`/
`description`), which is all `DiscountHistoryRepository` relies on.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any
from urllib.parse import urlparse


class UnsupportedDialectError(ValueError):
    def __init__(self, dialect: str) -> None:
        super().__init__(f"Unsupported dialect: {dialect!r}")


def build_connection() -> Any:
    dialect = os.environ.get("DB_DIALECT", "sqlite")
    dsn = os.environ.get("DB_DSN", "discount_strategy_api.db")

    if dialect == "sqlite":
        return sqlite3.connect(dsn)
    if dialect == "mysql":
        return _connect_mysql(dsn)
    raise UnsupportedDialectError(dialect)


def _connect_mysql(dsn: str) -> Any:
    import pymysql

    parsed = urlparse(dsn)
    return pymysql.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 3306,
        user=parsed.username or "root",
        password=parsed.password or "",
        database=parsed.path.lstrip("/"),
    )
