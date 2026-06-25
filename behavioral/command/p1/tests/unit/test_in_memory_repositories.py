"""Unit tests for the in-memory repository adapters."""

from __future__ import annotations

from document_editor.domain.entities import CommandInfo, Document
from document_editor.infrastructure.in_memory_document_repository import (
    InMemoryCommandHistoryRepository,
    InMemoryDocumentRepository,
)


class TestInMemoryDocumentRepository:
    def test_get_returns_none_when_absent(self) -> None:
        repo = InMemoryDocumentRepository()

        assert repo.get("missing") is None

    def test_save_then_get_roundtrips(self) -> None:
        repo = InMemoryDocumentRepository()
        document = Document(document_id="doc-1", content="hello")

        repo.save(document)

        assert repo.get("doc-1") is document


class TestInMemoryCommandHistoryRepository:
    def test_list_for_document_filters_by_id(self) -> None:
        repo = InMemoryCommandHistoryRepository()
        info_a = CommandInfo(command_id="a", description="cmd a", is_reversible=True)
        info_b = CommandInfo(command_id="b", description="cmd b", is_reversible=True)
        repo.append("doc-1", info_a, "execute")
        repo.append("doc-2", info_b, "execute")

        result = repo.list_for_document("doc-1")

        assert result == [info_a]
