"""SQLite-backed EditorCaretaker — persists snapshots and the undo/redo
pointer across CLI invocations (each command is a separate process).

Schema:
- `snapshot`: append-only log of every content version ever written.
- `pointer`: a single row tracking which snapshot id the document is
  currently restored to. `undo`/`redo` move this pointer without
  touching the log; `write` truncates any snapshots ahead of the
  pointer (the classic "writing after undo discards redo history").
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from text_editor_memento.domain.entities import NoHistoryError, TextSnapshot
from text_editor_memento.domain.interfaces import EditorCaretaker

_SNAPSHOT_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""

_POINTER_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS pointer (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_id INTEGER
)
"""


class SqliteEditorCaretaker(EditorCaretaker):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(_SNAPSHOT_TABLE_SQL)
        self._connection.execute(_POINTER_TABLE_SQL)
        self._connection.commit()

    def write(self, content: str) -> TextSnapshot:
        current_id = self._current_id()
        if current_id is not None:
            self._connection.execute("DELETE FROM snapshot WHERE id > ?", (current_id,))
        created_at = datetime.now(UTC)
        cursor = self._connection.execute(
            "INSERT INTO snapshot (content, created_at) VALUES (?, ?)",
            (content, created_at.isoformat()),
        )
        new_id = int(cursor.lastrowid or 0)
        self._set_pointer(new_id)
        self._connection.commit()
        return TextSnapshot(content=content, version=new_id, created_at=created_at)

    def undo(self) -> TextSnapshot:
        current_id = self._current_id()
        if current_id is None:
            raise NoHistoryError("undo")
        row = self._connection.execute(
            "SELECT id FROM snapshot WHERE id < ? ORDER BY id DESC LIMIT 1",
            (current_id,),
        ).fetchone()
        if row is None:
            raise NoHistoryError("undo")
        self._set_pointer(row[0])
        self._connection.commit()
        return self._fetch(row[0])

    def redo(self) -> TextSnapshot:
        current_id = self._current_id()
        query_id = current_id if current_id is not None else 0
        row = self._connection.execute(
            "SELECT id FROM snapshot WHERE id > ? ORDER BY id ASC LIMIT 1",
            (query_id,),
        ).fetchone()
        if row is None:
            raise NoHistoryError("redo")
        self._set_pointer(row[0])
        self._connection.commit()
        return self._fetch(row[0])

    def current(self) -> TextSnapshot:
        current_id = self._current_id()
        if current_id is None:
            raise NoHistoryError("read")
        return self._fetch(current_id)

    def history(self) -> list[TextSnapshot]:
        rows = self._connection.execute(
            "SELECT id, content, created_at FROM snapshot ORDER BY id ASC"
        ).fetchall()
        return [
            TextSnapshot(
                content=row[1],
                version=row[0],
                created_at=datetime.fromisoformat(row[2]),
            )
            for row in rows
        ]

    def _current_id(self) -> int | None:
        row = self._connection.execute(
            "SELECT current_id FROM pointer WHERE id = 1"
        ).fetchone()
        return None if row is None else row[0]

    def _set_pointer(self, snapshot_id: int) -> None:
        self._connection.execute(
            "INSERT INTO pointer (id, current_id) VALUES (1, ?) "
            "ON CONFLICT(id) DO UPDATE SET current_id = excluded.current_id",
            (snapshot_id,),
        )

    def _fetch(self, snapshot_id: int) -> TextSnapshot:
        row = self._connection.execute(
            "SELECT content, created_at FROM snapshot WHERE id = ?", (snapshot_id,)
        ).fetchone()
        assert row is not None
        return TextSnapshot(
            content=row[0],
            version=snapshot_id,
            created_at=datetime.fromisoformat(row[1]),
        )
