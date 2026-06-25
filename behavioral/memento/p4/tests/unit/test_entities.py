"""Unit tests for TextDocument and TextSnapshot domain entities."""

from __future__ import annotations

import pytest

from text_editor_memento.domain.entities import TextDocument, TextSnapshot


def test_snapshot_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="version"):
        TextSnapshot(content="x", version=0)


def test_create_snapshot_captures_current_content() -> None:
    document = TextDocument(content="hello")

    snapshot = document.create_snapshot(version=1)

    assert snapshot.content == "hello"
    assert snapshot.version == 1


def test_restore_replaces_content_and_version() -> None:
    document = TextDocument(content="hello")
    snapshot = TextSnapshot(content="world", version=5)

    document.restore(snapshot)

    assert document.content == "world"
    assert document.current_version == 5


def test_write_replaces_content() -> None:
    document = TextDocument(content="hello")

    document.write("goodbye")

    assert document.content == "goodbye"
