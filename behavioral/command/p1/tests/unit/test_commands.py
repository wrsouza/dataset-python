"""Unit tests for the concrete Command implementations."""

from __future__ import annotations

import pytest

from document_editor.application.commands import (
    DeleteTextCommand,
    FormatCommand,
    InsertTextCommand,
)
from document_editor.domain.entities import (
    Document,
    InvalidPositionError,
    InvalidRangeError,
)


class TestInsertTextCommand:
    def test_execute_inserts_text_at_position(self, document: Document) -> None:
        command = InsertTextCommand(document, position=0, text="hello")

        result = command.execute()

        assert document.get_content() == "hello"
        assert result.success is True
        assert result.content_snapshot == "hello"

    def test_undo_removes_previously_inserted_text(self, document: Document) -> None:
        document.insert(0, "hello world")
        command = InsertTextCommand(document, position=5, text=" there")
        command.execute()

        command.undo()

        assert document.get_content() == "hello world"

    def test_execute_raises_for_out_of_bounds_position(
        self, document: Document
    ) -> None:
        command = InsertTextCommand(document, position=99, text="x")

        with pytest.raises(InvalidPositionError):
            command.execute()

    def test_is_reversible(self, document: Document) -> None:
        command = InsertTextCommand(document, position=0, text="x")

        assert command.is_reversible() is True

    def test_get_description_mentions_position(self, document: Document) -> None:
        command = InsertTextCommand(document, position=3, text="abc")

        assert "3" in command.get_description()


class TestDeleteTextCommand:
    def test_execute_deletes_range_and_returns_remaining_content(
        self, document: Document
    ) -> None:
        document.insert(0, "hello world")
        command = DeleteTextCommand(document, start=5, end=11)

        result = command.execute()

        assert document.get_content() == "hello"
        assert result.content_snapshot == "hello"

    def test_undo_reinserts_deleted_text(self, document: Document) -> None:
        document.insert(0, "hello world")
        command = DeleteTextCommand(document, start=0, end=6)
        command.execute()

        command.undo()

        assert document.get_content() == "hello world"

    def test_execute_raises_for_invalid_range(self, document: Document) -> None:
        document.insert(0, "abc")
        command = DeleteTextCommand(document, start=5, end=10)

        with pytest.raises(InvalidRangeError):
            command.execute()


class TestFormatCommand:
    def test_execute_applies_format_range(self, document: Document) -> None:
        document.insert(0, "hello world")
        command = FormatCommand(document, start=0, end=5, format_type="bold")

        command.execute()

        ranges = document.get_formatted_ranges()
        assert {"start": 0, "end": 5, "format_type": "bold"} in ranges

    def test_undo_removes_format_range(self, document: Document) -> None:
        document.insert(0, "hello world")
        command = FormatCommand(document, start=0, end=5, format_type="italic")
        command.execute()

        command.undo()

        assert document.get_formatted_ranges() == []
