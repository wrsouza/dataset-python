"""Domain entities for the document cloner system."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DocumentRecord:
    """A persisted document in MongoDB."""

    id: str  # MongoDB ObjectId as string
    template_id: str
    doc_type: str
    title: str
    content: str
    metadata: dict[str, str]
    substitutions: dict[str, str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TemplateRecord:
    """A persisted template in MongoDB."""

    id: str
    doc_type: str
    title: str
    content: str
    metadata: dict[str, str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class TemplateNotFoundError(Exception):
    """Raised when a document template is not found."""

    def __init__(self, template_id: str) -> None:
        self.template_id = template_id
        super().__init__(f"Template '{template_id}' not found")


class DocumentNotFoundError(Exception):
    """Raised when a document is not found."""

    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(f"Document '{document_id}' not found")
