"""Unit tests for SqliteEditorCaretaker."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from text_editor_memento.domain.entities import NoHistoryError
from text_editor_memento.infrastructure.sqlite_caretaker import SqliteEditorCaretaker


@pytest.fixture
def caretaker() -> Iterator[SqliteEditorCaretaker]:
    connection = sqlite3.connect(":memory:")
    try:
        yield SqliteEditorCaretaker(connection)
    finally:
        connection.close()


def test_write_returns_snapshot_with_content(caretaker: SqliteEditorCaretaker) -> None:
    snapshot = caretaker.write("hello")

    assert snapshot.content == "hello"
    assert snapshot.version == 1


def test_current_raises_before_any_write(caretaker: SqliteEditorCaretaker) -> None:
    with pytest.raises(NoHistoryError):
        caretaker.current()


def test_current_returns_latest_write(caretaker: SqliteEditorCaretaker) -> None:
    caretaker.write("hello")
    caretaker.write("world")

    current = caretaker.current()

    assert current.content == "world"


def test_undo_reverts_to_previous_snapshot(caretaker: SqliteEditorCaretaker) -> None:
    caretaker.write("hello")
    caretaker.write("world")

    restored = caretaker.undo()

    assert restored.content == "hello"


def test_undo_raises_when_nothing_written(caretaker: SqliteEditorCaretaker) -> None:
    with pytest.raises(NoHistoryError):
        caretaker.undo()


def test_undo_raises_when_already_at_first_snapshot(
    caretaker: SqliteEditorCaretaker,
) -> None:
    caretaker.write("hello")

    with pytest.raises(NoHistoryError):
        caretaker.undo()


def test_redo_reapplies_undone_snapshot(caretaker: SqliteEditorCaretaker) -> None:
    caretaker.write("hello")
    caretaker.write("world")
    caretaker.undo()

    restored = caretaker.redo()

    assert restored.content == "world"


def test_redo_raises_when_nothing_to_redo(caretaker: SqliteEditorCaretaker) -> None:
    caretaker.write("hello")

    with pytest.raises(NoHistoryError):
        caretaker.redo()


def test_write_after_undo_discards_redo_branch(
    caretaker: SqliteEditorCaretaker,
) -> None:
    caretaker.write("hello")
    caretaker.write("world")
    caretaker.undo()

    caretaker.write("goodbye")

    with pytest.raises(NoHistoryError):
        caretaker.redo()
    assert [s.content for s in caretaker.history()] == ["hello", "goodbye"]


def test_history_returns_all_snapshots_in_order(
    caretaker: SqliteEditorCaretaker,
) -> None:
    caretaker.write("a")
    caretaker.write("b")
    caretaker.write("c")

    history = caretaker.history()

    assert [s.content for s in history] == ["a", "b", "c"]
