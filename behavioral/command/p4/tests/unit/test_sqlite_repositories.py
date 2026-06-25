"""Unit tests for the SQLite-backed state and log repositories."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from cli_history.domain.entities import TodoList
from cli_history.infrastructure.sqlite_repositories import (
    SqliteCommandLogRepository,
    SqliteStateRepository,
)


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_state_repository_load_returns_empty_list_initially(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteStateRepository(connection)

    assert repository.load() == TodoList()


def test_state_repository_save_and_load_round_trips(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteStateRepository(connection)

    repository.save(TodoList(items=["a", "b"]))

    assert repository.load().items == ["a", "b"]


def test_state_repository_save_overwrites_previous_state(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteStateRepository(connection)
    repository.save(TodoList(items=["a"]))

    repository.save(TodoList(items=["a", "b"]))

    assert repository.load().items == ["a", "b"]


def test_log_repository_append_assigns_incrementing_ids(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteCommandLogRepository(connection)

    first = repository.append("add", {"item": "a"})
    second = repository.append("add", {"item": "b"})

    assert second.entry_id > first.entry_id


def test_log_repository_get_all_returns_entries_in_order(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteCommandLogRepository(connection)
    repository.append("add", {"item": "a"})
    repository.append("remove", {"item": "a"})

    entries = repository.get_all()

    assert [e.command_name for e in entries] == ["add", "remove"]


def test_log_repository_get_all_returns_empty_list_initially(
    connection: sqlite3.Connection,
) -> None:
    repository = SqliteCommandLogRepository(connection)

    assert repository.get_all() == []
