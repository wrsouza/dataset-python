"""SQLite-backed implementations of StateRepository and CommandLogRepository."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from cli_history.domain.entities import CommandLogEntry, TodoList
from cli_history.domain.interfaces import CommandLogRepository, StateRepository

_STATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS todo_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    items_json TEXT NOT NULL
)
"""

_LOG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS command_log (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_name TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    executed_at TEXT NOT NULL
)
"""


class SqliteStateRepository(StateRepository):
    """Persists the single live TodoList snapshot in a SQLite table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(_STATE_TABLE_SQL)
        self._connection.commit()

    def load(self) -> TodoList:
        row = self._connection.execute(
            "SELECT items_json FROM todo_state WHERE id = 1"
        ).fetchone()
        if row is None:
            return TodoList()
        return TodoList(items=json.loads(row[0]))

    def save(self, state: TodoList) -> None:
        self._connection.execute(
            "INSERT INTO todo_state (id, items_json) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET items_json = excluded.items_json",
            (json.dumps(state.items),),
        )
        self._connection.commit()


class SqliteCommandLogRepository(CommandLogRepository):
    """Appends and reads the command execution log from a SQLite table."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(_LOG_TABLE_SQL)
        self._connection.commit()

    def append(self, command_name: str, payload: dict[str, object]) -> CommandLogEntry:
        executed_at = datetime.now(UTC)
        cursor = self._connection.execute(
            "INSERT INTO command_log (command_name, payload_json, executed_at) "
            "VALUES (?, ?, ?)",
            (command_name, json.dumps(payload), executed_at.isoformat()),
        )
        self._connection.commit()
        return CommandLogEntry(
            entry_id=int(cursor.lastrowid or 0),
            command_name=command_name,
            payload=payload,
            executed_at=executed_at,
        )

    def get_all(self) -> list[CommandLogEntry]:
        rows = self._connection.execute(
            "SELECT entry_id, command_name, payload_json, executed_at "
            "FROM command_log ORDER BY entry_id ASC"
        ).fetchall()
        return [
            CommandLogEntry(
                entry_id=row[0],
                command_name=row[1],
                payload=json.loads(row[2]),
                executed_at=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]
