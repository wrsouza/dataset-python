"""Unit tests for the Document receiver entity."""

from __future__ import annotations

import pytest

from document_editor.domain.entities import (
    Document,
    InvalidPositionError,
    InvalidRangeError,
)


class TestDocument:
    def test_insert_appends_at_position(self, document: Document) -> None:
        document.insert(0, "abc")
        document.insert(3, "def")

        assert document.get_content() == "abcdef"

    def test_insert_out_of_bounds_raises(self, document: Document) -> None:
        with pytest.raises(InvalidPositionError):
            document.insert(10, "x")

    def test_delete_returns_removed_text(self, document: Document) -> None:
        document.insert(0, "abcdef")

        removed = document.delete(1, 3)

        assert removed == "bc"
        assert document.get_content() == "adef"

    def test_delete_invalid_range_raises(self, document: Document) -> None:
        document.insert(0, "abc")

        with pytest.raises(InvalidRangeError):
            document.delete(2, 1)

    def test_apply_and_remove_format(self, document: Document) -> None:
        document.insert(0, "hello")
        document.apply_format(0, 5, "bold")

        assert document.get_formatted_ranges() == [
            {"start": 0, "end": 5, "format_type": "bold"}
        ]

        document.remove_format(0, 5, "bold")

        assert document.get_formatted_ranges() == []
