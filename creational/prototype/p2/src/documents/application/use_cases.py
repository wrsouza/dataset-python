"""Application use cases for the document cloner.

SRP: each use case has one purpose.
DIP: depends on repository interfaces, not concrete MongoDB classes.
"""
from __future__ import annotations

from documents.domain.entities import DocumentRecord, TemplateRecord
from documents.infrastructure.mongodb import MongoDocumentRepository, MongoTemplateRepository
from documents.infrastructure.prototypes import get_template_by_type


class CreateTemplateUseCase:
    """Create and persist a new document template.

    SRP: only responsible for template creation.
    """

    def __init__(self, repo: MongoTemplateRepository) -> None:
        self._repo = repo

    def execute(
        self,
        doc_type: str,
        title: str,
        content: str,
        metadata: dict[str, str],
    ) -> TemplateRecord:
        """Validate doc type and persist the template."""
        # Validate that we have a prototype for this type
        get_template_by_type(doc_type)
        return self._repo.save(doc_type, title, content, metadata)


class ListTemplatesUseCase:
    """List all available templates."""

    def __init__(self, repo: MongoTemplateRepository) -> None:
        self._repo = repo

    def execute(self) -> list[TemplateRecord]:
        """Return all stored templates."""
        return self._repo.find_all()


class CloneDocumentUseCase:
    """Clone a template with substitutions and persist the result.

    This is the core Prototype operation:
    1. Load template from MongoDB
    2. Get the ConcretePrototype for its doc_type
    3. Populate the prototype with template content
    4. Call clone(substitutions) → deep copy + placeholder replacement
    5. Persist the cloned document
    """

    def __init__(
        self,
        template_repo: MongoTemplateRepository,
        document_repo: MongoDocumentRepository,
    ) -> None:
        self._template_repo = template_repo
        self._document_repo = document_repo

    def execute(
        self, template_id: str, substitutions: dict[str, str]
    ) -> DocumentRecord:
        """Load the template, clone it with substitutions, and persist."""
        template_record = self._template_repo.find_by_id(template_id)

        # Build a prototype from the stored template
        prototype = get_template_by_type(template_record.doc_type)
        # Override the prototype's content with the stored template's content
        prototype._title = template_record.title  # type: ignore[attr-defined]
        prototype._content = template_record.content  # type: ignore[attr-defined]
        prototype._metadata = dict(template_record.metadata)  # type: ignore[attr-defined]

        # Clone: deepcopy + apply substitutions
        cloned = prototype.clone(substitutions)

        return self._document_repo.save(
            template_id=template_id,
            doc_type=cloned.doc_type,
            title=cloned.title,
            content=cloned.content,
            metadata=cloned.metadata,
            substitutions=substitutions,
        )


class GetDocumentUseCase:
    """Retrieve a single persisted document."""

    def __init__(self, repo: MongoDocumentRepository) -> None:
        self._repo = repo

    def execute(self, document_id: str) -> DocumentRecord:
        """Return the document with the given id."""
        return self._repo.find_by_id(document_id)
