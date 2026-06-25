"""PostgreSQL-backed implementations of the domain repositories.

These are the only modules in the codebase that know about SQLAlchemy —
the domain and application layers depend solely on the abstractions in
`document_editor.domain.repositories` (Dependency Inversion).
"""

from __future__ import annotations

from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from document_editor.domain.entities import (
    CommandInfo,
    Document,
    FormatRange,
    FormatType,
)
from document_editor.domain.repositories import (
    CommandHistoryRepository,
    DocumentRepository,
)
from document_editor.infrastructure.models import CommandHistoryModel, DocumentModel


class PostgresDocumentRepository(DocumentRepository):
    """Stores `Document` aggregates in the `documents` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, document_id: str) -> Document | None:
        row = self._session.get(DocumentModel, document_id)
        if row is None:
            return None
        return Document(
            document_id=row.document_id,
            content=row.content,
            format_ranges=[
                FormatRange(
                    start=cast(int, r["start"]),
                    end=cast(int, r["end"]),
                    format_type=FormatType(cast(str, r["format_type"])),
                )
                for r in row.format_ranges
            ],
        )

    def save(self, document: Document) -> None:
        row = self._session.get(DocumentModel, document.document_id)
        ranges: list[dict[str, object]] = [
            {"start": r.start, "end": r.end, "format_type": r.format_type.value}
            for r in document.format_ranges
        ]
        if row is None:
            row = DocumentModel(
                document_id=document.document_id,
                content=document.content,
                format_ranges=ranges,
            )
            self._session.add(row)
        else:
            row.content = document.content
            row.format_ranges = ranges
        self._session.commit()


class PostgresCommandHistoryRepository(CommandHistoryRepository):
    """Stores command history entries in the `command_history` table."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, document_id: str, info: CommandInfo, action: str) -> None:
        row = CommandHistoryModel(
            command_id=info.command_id,
            document_id=document_id,
            description=info.description,
            is_reversible=info.is_reversible,
            action=action,
            executed_at=info.executed_at,
        )
        self._session.add(row)
        self._session.commit()

    def list_for_document(self, document_id: str) -> list[CommandInfo]:
        statement = select(CommandHistoryModel).where(
            CommandHistoryModel.document_id == document_id
        )
        rows = self._session.scalars(statement).all()
        return [
            CommandInfo(
                command_id=row.command_id,
                description=row.description,
                is_reversible=row.is_reversible,
                executed_at=row.executed_at,
            )
            for row in rows
        ]
