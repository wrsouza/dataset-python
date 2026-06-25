"""Composition helpers for wiring repositories to a real SQLite file."""

from __future__ import annotations

import os
import sqlite3

from cli_history.infrastructure.sqlite_repositories import (
    SqliteCommandLogRepository,
    SqliteStateRepository,
)


def build_connection() -> sqlite3.Connection:
    """Open the SQLite database file used to persist state and history."""
    db_path = os.environ.get("CLI_HISTORY_DB_PATH", "cli_history.db")
    return sqlite3.connect(db_path)


def build_state_repository(connection: sqlite3.Connection) -> SqliteStateRepository:
    return SqliteStateRepository(connection)


def build_log_repository(connection: sqlite3.Connection) -> SqliteCommandLogRepository:
    return SqliteCommandLogRepository(connection)
