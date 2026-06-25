"""Unit tests for document use cases with in-memory fakes."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from documents.application.use_cases import (
    CloneDocumentUseCase,
    CreateTemplateUseCase,
    GetDocumentUseCase,
    ListTemplatesUseCase,
)
from documents.domain.entities import (
    DocumentNotFoundError,
    DocumentRecord,
    TemplateNotFoundError,
    TemplateRecord,
)


def make_template(id: str = "abc123", doc_type: str = "contract") -> TemplateRecord:
    return TemplateRecord(
        id=id,
        doc_type=doc_type,
        title="Test Contract — {{client_name}}",
        content="This is a contract for {{client_name}}.",
        metadata={},
        created_at=datetime.utcnow(),
    )


def make_document(id: str = "doc123") -> DocumentRecord:
    return DocumentRecord(
        id=id,
        template_id="abc123",
        doc_type="contract",
        title="Test Contract — Acme",
        content="This is a contract for Acme.",
        metadata={},
        substitutions={"client_name": "Acme"},
        created_at=datetime.utcnow(),
    )


class TestCreateTemplateUseCase:
    def test_creates_valid_template(self) -> None:
        repo = MagicMock()
        repo.save.return_value = make_template()
        use_case = CreateTemplateUseCase(repo)
        result = use_case.execute("contract", "Title", "Content {{x}}", {})
        repo.save.assert_called_once()
        assert result.id == "abc123"

    def test_unknown_doc_type_raises(self) -> None:
        repo = MagicMock()
        use_case = CreateTemplateUseCase(repo)
        with pytest.raises(ValueError):
            use_case.execute("invoice", "Title", "Content", {})


class TestListTemplatesUseCase:
    def test_returns_all_templates(self) -> None:
        repo = MagicMock()
        repo.find_all.return_value = [make_template("1"), make_template("2")]
        use_case = ListTemplatesUseCase(repo)
        result = use_case.execute()
        assert len(result) == 2


class TestCloneDocumentUseCase:
    def test_clone_applies_substitutions(self) -> None:
        template_repo = MagicMock()
        template_repo.find_by_id.return_value = make_template()
        document_repo = MagicMock()
        document_repo.save.return_value = make_document()

        use_case = CloneDocumentUseCase(template_repo, document_repo)
        result = use_case.execute("abc123", {"client_name": "Acme"})

        document_repo.save.assert_called_once()
        assert result.id == "doc123"

    def test_template_not_found_propagates(self) -> None:
        template_repo = MagicMock()
        template_repo.find_by_id.side_effect = TemplateNotFoundError("missing")
        document_repo = MagicMock()
        use_case = CloneDocumentUseCase(template_repo, document_repo)
        with pytest.raises(TemplateNotFoundError):
            use_case.execute("missing", {})


class TestGetDocumentUseCase:
    def test_returns_document(self) -> None:
        repo = MagicMock()
        repo.find_by_id.return_value = make_document()
        use_case = GetDocumentUseCase(repo)
        result = use_case.execute("doc123")
        assert result.id == "doc123"

    def test_not_found_raises(self) -> None:
        repo = MagicMock()
        repo.find_by_id.side_effect = DocumentNotFoundError("missing")
        use_case = GetDocumentUseCase(repo)
        with pytest.raises(DocumentNotFoundError):
            use_case.execute("missing")
