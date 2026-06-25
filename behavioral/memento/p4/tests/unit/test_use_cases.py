"""Unit tests for Text Editor Undo/Redo use cases."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator

import pytest

from text_editor_memento.application.use_cases import (
    GetCurrentContentUseCase,
    GetHistoryUseCase,
    RedoEditUseCase,
    UndoEditUseCase,
    WriteContentUseCase,
)
from text_editor_memento.domain.entities import NoHistoryError
from text_editor_memento.infrastructure.sqlite_caretaker import SqliteEditorCaretaker


@pytest.fixture
def caretaker() -> Iterator[SqliteEditorCaretaker]:
    connection = sqlite3.connect(":memory:")
    try:
        yield SqliteEditorCaretaker(connection)
    finally:
        connection.close()


def test_write_content_use_case(caretaker: SqliteEditorCaretaker) -> None:
    use_case = WriteContentUseCase(caretaker)

    snapshot = use_case.execute("hello")

    assert snapshot.content == "hello"


def test_get_current_content_before_any_write_returns_empty(
    caretaker: SqliteEditorCaretaker,
) -> None:
    use_case = GetCurrentContentUseCase(caretaker)

    document = use_case.execute()

    assert document.content == ""


def test_get_current_content_after_write(caretaker: SqliteEditorCaretaker) -> None:
    WriteContentUseCase(caretaker).execute("hello")

    document = GetCurrentContentUseCase(caretaker).execute()

    assert document.content == "hello"


def test_undo_edit_use_case(caretaker: SqliteEditorCaretaker) -> None:
    write = WriteContentUseCase(caretaker)
    write.execute("hello")
    write.execute("world")

    snapshot = UndoEditUseCase(caretaker).execute()

    assert snapshot.content == "hello"


def test_undo_edit_use_case_raises_without_history(
    caretaker: SqliteEditorCaretaker,
) -> None:
    with pytest.raises(NoHistoryError):
        UndoEditUseCase(caretaker).execute()


def test_redo_edit_use_case(caretaker: SqliteEditorCaretaker) -> None:
    write = WriteContentUseCase(caretaker)
    write.execute("hello")
    write.execute("world")
    UndoEditUseCase(caretaker).execute()

    snapshot = RedoEditUseCase(caretaker).execute()

    assert snapshot.content == "world"


def test_get_history_use_case(caretaker: SqliteEditorCaretaker) -> None:
    write = WriteContentUseCase(caretaker)
    write.execute("hello")
    write.execute("world")

    history = GetHistoryUseCase(caretaker).execute()

    assert [s.content for s in history] == ["hello", "world"]
