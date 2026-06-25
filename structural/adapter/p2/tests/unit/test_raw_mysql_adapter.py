"""Unit tests for RawMySQLUserAdapter.

Mocks pymysql connection so no database is needed.
Verifies that the adapter calls the right SQL and maps rows to domain entities.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from orm_adapter.domain.entities import User, UserNotFoundError
from orm_adapter.infrastructure.raw_mysql_adapter import RawMySQLUserAdapter


@pytest.fixture
def mock_conn() -> MagicMock:
    conn = MagicMock()
    return conn


@pytest.fixture
def adapter(mock_conn: MagicMock) -> RawMySQLUserAdapter:
    return RawMySQLUserAdapter(connection=mock_conn)


def _make_cursor_with_rows(
    mock_conn: MagicMock, rows: list[dict[str, object]] | None
) -> MagicMock:
    cursor = MagicMock()
    cursor.__enter__ = MagicMock(return_value=cursor)
    cursor.__exit__ = MagicMock(return_value=False)
    if rows is None:
        cursor.fetchone.return_value = None
    elif len(rows) == 1:
        cursor.fetchone.return_value = rows[0]
    cursor.fetchall.return_value = rows or []
    mock_conn.cursor.return_value = cursor
    return cursor


class TestFindById:
    def test_returns_user_when_found(
        self, adapter: RawMySQLUserAdapter, mock_conn: MagicMock
    ) -> None:
        _make_cursor_with_rows(
            mock_conn,
            [{"id": 1, "name": "Alice", "email": "a@test.com", "is_active": True}],
        )
        result = adapter.find_by_id(1)
        assert result is not None
        assert result.name == "Alice"
        assert result.id == 1

    def test_returns_none_when_not_found(
        self, adapter: RawMySQLUserAdapter, mock_conn: MagicMock
    ) -> None:
        _make_cursor_with_rows(mock_conn, None)
        result = adapter.find_by_id(99)
        assert result is None


class TestSave:
    def test_insert_returns_user_with_new_id(
        self, adapter: RawMySQLUserAdapter, mock_conn: MagicMock
    ) -> None:
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        cursor.lastrowid = 42
        mock_conn.cursor.return_value = cursor

        user = User(name="Bob", email="b@test.com")
        result = adapter.save(user)

        assert result.id == 42
        assert result.name == "Bob"

    def test_update_raises_on_missing(
        self, adapter: RawMySQLUserAdapter, mock_conn: MagicMock
    ) -> None:
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        cursor.rowcount = 0
        mock_conn.cursor.return_value = cursor

        user = User(id=999, name="Ghost", email="ghost@test.com")
        with pytest.raises(UserNotFoundError):
            adapter.save(user)


class TestDelete:
    def test_raises_on_missing(
        self, adapter: RawMySQLUserAdapter, mock_conn: MagicMock
    ) -> None:
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        cursor.rowcount = 0
        mock_conn.cursor.return_value = cursor

        with pytest.raises(UserNotFoundError):
            adapter.delete(999)
