"""Composition helpers — builds the concrete SQLite connection from env vars."""

from __future__ import annotations

import os
import sqlite3


def build_connection() -> sqlite3.Connection:
    path = os.environ.get("TEXT_EDITOR_DB_PATH", "text_editor.db")
    return sqlite3.connect(path)
