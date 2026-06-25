"""Unit tests for Document Memento pattern — no database required."""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest

from documents.domain.entities import (
    Document,
    DocumentMemento,
    NoHistoryError,
    VersionNotFoundError,
)


class TestDocumentMemento:
    """DocumentMemento is immutable (frozen=True)."""

    def test_memento_is_frozen(self) -> None:
        memento = DocumentMemento(
            content="Hello",
            metadata={"tag": "draft"},
            version=1,
            author="alice",
        )
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            memento.content = "tampered"  # type: ignore[misc]

    def test_memento_rejects_zero_version(self) -> None:
        with pytest.raises(ValueError, match="version must be >= 1"):
            DocumentMemento(content="x", metadata={}, version=0, author="alice")

    def test_memento_rejects_empty_author(self) -> None:
        with pytest.raises(ValueError, match="author cannot be empty"):
            DocumentMemento(content="x", metadata={}, version=1, author="  ")

    def test_memento_stores_deep_copy_of_metadata(self) -> None:
        original_meta: dict = {"key": "value"}
        memento = DocumentMemento(
            content="text",
            metadata=original_meta,
            version=1,
            author="bob",
        )
        original_meta["key"] = "mutated"
        # frozen dataclass stores the dict but we passed a copy in entities.py
        assert memento.metadata == {"key": "value"}

    def test_memento_has_utc_timestamp_by_default(self) -> None:
        memento = DocumentMemento(content="x", metadata={}, version=1, author="alice")
        assert memento.created_at.tzinfo is not None


class TestDocumentOriginator:
    """Document (Originator) creates and restores snapshots correctly."""

    def _make_document(self) -> Document:
        return Document(
            id="doc-1",
            title="Test Doc",
            content="Initial content",
            metadata={"status": "draft"},
        )

    def test_create_snapshot_captures_current_state(self) -> None:
        doc = self._make_document()
        doc.set_author("alice")
        snapshot = doc.create_snapshot()

        assert snapshot.content == "Initial content"
        assert snapshot.metadata == {"status": "draft"}
        assert snapshot.version == 1
        assert snapshot.author == "alice"

    def test_restore_returns_exact_snapshot_state(self) -> None:
        doc = self._make_document()
        doc.set_author("alice")
        snapshot = doc.create_snapshot()

        # Apply changes
        doc.apply_edit("New content", {"status": "published"})
        assert doc.content == "New content"
        assert doc.current_version == 2

        # Restore
        doc.restore(snapshot)
        assert doc.content == snapshot.content
        assert doc.metadata == snapshot.metadata
        assert doc.current_version == snapshot.version

    def test_restore_does_not_mutate_memento(self) -> None:
        doc = self._make_document()
        doc.set_author("alice")
        snapshot = doc.create_snapshot()

        doc.apply_edit("Modified", {"status": "review"})
        doc.restore(snapshot)

        # The memento should be unchanged
        assert snapshot.content == "Initial content"
        assert snapshot.version == 1

    def test_metadata_is_deep_copied_on_restore(self) -> None:
        doc = self._make_document()
        doc.set_author("alice")
        snapshot = doc.create_snapshot()

        doc.restore(snapshot)
        # Mutate restored metadata — should not affect the memento
        doc.metadata["injected"] = True
        assert "injected" not in snapshot.metadata

    def test_apply_edit_increments_version(self) -> None:
        doc = self._make_document()
        assert doc.current_version == 1
        doc.apply_edit("v2", {})
        assert doc.current_version == 2
        doc.apply_edit("v3", {})
        assert doc.current_version == 3

    def test_multiple_snapshots_are_independent(self) -> None:
        doc = self._make_document()
        doc.set_author("alice")
        snap1 = doc.create_snapshot()

        doc.apply_edit("Content v2", {"status": "review"})
        doc.set_author("bob")
        snap2 = doc.create_snapshot()

        assert snap1.content != snap2.content
        assert snap1.version != snap2.version
        assert snap1.author == "alice"
        assert snap2.author == "bob"


class TestVersionNotFoundError:
    def test_error_message(self) -> None:
        err = VersionNotFoundError("doc-1", 99)
        assert "99" in str(err)
        assert "doc-1" in str(err)


class TestNoHistoryError:
    def test_error_message(self) -> None:
        err = NoHistoryError("doc-1")
        assert "doc-1" in str(err)
