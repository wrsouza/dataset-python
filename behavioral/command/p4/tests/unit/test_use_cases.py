"""Unit tests for the execute/undo/history/replay use cases."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from cli_history.application.use_cases import (
    ExecuteCommandUseCase,
    GetHistoryUseCase,
    ReplayHistoryUseCase,
    UndoLastCommandUseCase,
)
from cli_history.infrastructure.sqlite_repositories import (
    SqliteCommandLogRepository,
    SqliteStateRepository,
)


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_execute_command_adds_item_and_logs_it(connection: sqlite3.Connection) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    use_case = ExecuteCommandUseCase(state_repo, log_repo)

    state = use_case.execute("add", {"item": "Buy milk"})

    assert state.items == ["Buy milk"]
    assert [e.command_name for e in log_repo.get_all()] == ["add"]


def test_execute_command_persists_state_across_use_case_instances(
    connection: sqlite3.Connection,
) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    ExecuteCommandUseCase(state_repo, log_repo).execute("add", {"item": "a"})

    second_state = ExecuteCommandUseCase(state_repo, log_repo).execute(
        "add", {"item": "b"}
    )

    assert second_state.items == ["a", "b"]


def test_undo_last_command_reverts_the_most_recent_add(
    connection: sqlite3.Connection,
) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    execute_use_case = ExecuteCommandUseCase(state_repo, log_repo)
    execute_use_case.execute("add", {"item": "a"})
    execute_use_case.execute("add", {"item": "b"})

    undo_use_case = UndoLastCommandUseCase(state_repo, log_repo)
    state = undo_use_case.execute()

    assert state.items == ["a"]


def test_undo_with_empty_history_is_noop(connection: sqlite3.Connection) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    undo_use_case = UndoLastCommandUseCase(state_repo, log_repo)

    state = undo_use_case.execute()

    assert state.items == []


def test_get_history_returns_entries_in_execution_order(
    connection: sqlite3.Connection,
) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    execute_use_case = ExecuteCommandUseCase(state_repo, log_repo)
    execute_use_case.execute("add", {"item": "a"})
    execute_use_case.execute("remove", {"item": "a"})

    history = GetHistoryUseCase(log_repo).execute()

    assert [e.command_name for e in history] == ["add", "remove"]


def test_replay_history_rebuilds_state_from_log_alone(
    connection: sqlite3.Connection,
) -> None:
    state_repo = SqliteStateRepository(connection)
    log_repo = SqliteCommandLogRepository(connection)
    execute_use_case = ExecuteCommandUseCase(state_repo, log_repo)
    execute_use_case.execute("add", {"item": "a"})
    execute_use_case.execute("add", {"item": "b"})
    execute_use_case.execute("remove", {"item": "a"})

    replayed = ReplayHistoryUseCase(log_repo).execute()

    assert replayed.items == ["b"]


def test_replay_history_with_empty_log_returns_empty_list(
    connection: sqlite3.Connection,
) -> None:
    log_repo = SqliteCommandLogRepository(connection)

    replayed = ReplayHistoryUseCase(log_repo).execute()

    assert replayed.items == []
