"""CLI integration tests via Typer's CliRunner — exercises the real entrypoint."""

from __future__ import annotations

import sqlite3

import pytest
from typer.testing import CliRunner

from migration.cli import (
    UnsupportedConnectionStringError,
    app,
    parse_connection_string,
)

runner = CliRunner()


def test_parse_connection_string_sqlite() -> None:
    config = parse_connection_string("sqlite:///tmp/test.db")
    assert config.dialect == "sqlite"
    assert config.dsn == "/tmp/test.db"


def test_parse_connection_string_mysql() -> None:
    config = parse_connection_string("mysql://user:pw@host/db")
    assert config.dialect == "mysql"


def test_parse_connection_string_postgresql() -> None:
    config = parse_connection_string("postgresql://user:pw@host/db")
    assert config.dialect == "postgresql"


def test_parse_connection_string_rejects_unknown_scheme() -> None:
    with pytest.raises(UnsupportedConnectionStringError):
        parse_connection_string("oracle://user:pw@host/db")


def test_cli_migrate_success(source_db_path: str, dest_db_path: str) -> None:
    result = runner.invoke(
        app,
        [
            "migrate",
            "--from",
            f"sqlite://{source_db_path}",
            "--to",
            f"sqlite://{dest_db_path}",
            "--tables",
            "orders",
        ],
    )

    assert result.exit_code == 0
    assert "SUCCESS" in result.stdout

    conn = sqlite3.connect(dest_db_path)
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    assert count == 3


def test_cli_migrate_failure_exits_nonzero(
    source_db_path: str, dest_db_path: str
) -> None:
    result = runner.invoke(
        app,
        [
            "migrate",
            "--from",
            f"sqlite://{source_db_path}",
            "--to",
            f"sqlite://{dest_db_path}",
            "--tables",
            "does_not_exist",
        ],
    )

    assert result.exit_code == 1
    assert "ROLLED BACK" in result.stdout


def test_cli_dry_run_reports_warning(source_db_path: str) -> None:
    result = runner.invoke(
        app,
        ["dry-run", "--from", f"sqlite://{source_db_path}", "--tables", "empty_table"],
    )

    assert result.exit_code == 0
    assert "WARNING" in result.stdout
    assert "VALID" in result.stdout


def test_cli_dry_run_invalid_exits_nonzero(source_db_path: str) -> None:
    result = runner.invoke(
        app,
        ["dry-run", "--from", f"sqlite://{source_db_path}", "--tables", "ghost_table"],
    )

    assert result.exit_code == 1
    assert "INVALID" in result.stdout
