"""Unit tests for the dialect-aware connection factory.

`pymysql.connect` isn't called against a real server here — `_connect_mysql`
is exercised by monkeypatching `pymysql.connect` itself, the same way a
real MySQL driver would be swapped out in any DB-API test.
"""

from __future__ import annotations

from typing import Any

import pytest

from discount_strategy_api.infrastructure.connection_factory import (
    UnsupportedDialectError,
    build_connection,
)


def test_build_connection_defaults_to_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DB_DIALECT", raising=False)
    monkeypatch.delenv("DB_DSN", raising=False)

    connection = build_connection()

    connection.execute("SELECT 1")
    connection.close()


def test_build_connection_mysql_dialect_uses_pymysql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}

    def fake_connect(**kwargs: Any) -> str:
        calls.update(kwargs)
        return "fake-connection"

    import pymysql

    monkeypatch.setattr(pymysql, "connect", fake_connect)
    monkeypatch.setenv("DB_DIALECT", "mysql")
    monkeypatch.setenv("DB_DSN", "mysql://user:pass@dbhost:3307/mydb")

    connection = build_connection()

    assert connection == "fake-connection"
    assert calls == {
        "host": "dbhost",
        "port": 3307,
        "user": "user",
        "password": "pass",
        "database": "mydb",
    }


def test_build_connection_rejects_unsupported_dialect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DB_DIALECT", "oracle")

    with pytest.raises(UnsupportedDialectError):
        build_connection()
