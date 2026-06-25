"""FastAPI application entry-point for the Document Editor service.

Exposes endpoints to apply Command pattern operations (insert/delete/format)
against a document, plus undo/redo over the Invoker's history stacks.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from document_editor.application.commands import (
    DeleteTextCommand,
    FormatCommand,
    InsertTextCommand,
)
from document_editor.application.use_cases import HistoryInvoker
from document_editor.domain.entities import Document
from document_editor.domain.interfaces import DocumentCommand
from document_editor.infrastructure.database import get_session, init_db
from document_editor.infrastructure.postgres_document_repository import (
    PostgresDocumentRepository,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Composition root: one Invoker per document, kept in process memory.
# Persisted document content/history lives in PostgreSQL via the repository.
_invokers: dict[str, HistoryInvoker] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Create database tables on application boot.

    Swallows connection errors so the app (and the test suite, which
    overrides `get_session` with SQLite) can start even when the
    PostgreSQL service declared in docker-compose is not reachable yet.
    """
    try:
        init_db()
    except Exception:  # noqa: BLE001 - startup must not crash the test client
        logger.warning("Could not initialize database tables at startup")
    yield


app = FastAPI(
    title="Document Editor — Undo/Redo API",
    description=(
        "Command pattern: DocumentCommand=insert/delete/format, "
        "Invoker=HistoryInvoker, Receiver=Document"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def _get_invoker(document_id: str) -> HistoryInvoker:
    if document_id not in _invokers:
        _invokers[document_id] = HistoryInvoker()
    return _invokers[document_id]


def _get_or_create_document(session: Session, document_id: str) -> Document:
    repo = PostgresDocumentRepository(session)
    document = repo.get(document_id)
    if document is None:
        document = Document(document_id=document_id)
        repo.save(document)
    return document


class InsertRequest(BaseModel):
    position: int
    text: str


class DeleteRequest(BaseModel):
    start: int
    end: int


class FormatRequest(BaseModel):
    start: int
    end: int
    format_type: Literal["bold", "italic", "underline"]


class DocumentStateResponse(BaseModel):
    document_id: str
    content: str
    format_ranges: list[dict[str, object]]


class CommandResultResponse(BaseModel):
    success: bool
    message: str
    content_snapshot: str


def _run_command(
    session: Session, document_id: str, document: Document, command: DocumentCommand
) -> CommandResultResponse:
    invoker = _get_invoker(document_id)
    result = invoker.execute(command)
    PostgresDocumentRepository(session).save(document)
    return CommandResultResponse(
        success=result.success,
        message=result.message,
        content_snapshot=result.content_snapshot,
    )


@app.get("/documents/{document_id}", response_model=DocumentStateResponse)
def get_document(
    document_id: str, session: Session = Depends(get_session)
) -> DocumentStateResponse:
    document = _get_or_create_document(session, document_id)
    return DocumentStateResponse(
        document_id=document.document_id,
        content=document.get_content(),
        format_ranges=document.get_formatted_ranges(),
    )


@app.post(
    "/documents/{document_id}/insert",
    response_model=CommandResultResponse,
    status_code=201,
)
def insert_text(
    document_id: str,
    request: InsertRequest,
    session: Session = Depends(get_session),
) -> CommandResultResponse:
    document = _get_or_create_document(session, document_id)
    command = InsertTextCommand(document, request.position, request.text)
    try:
        return _run_command(session, document_id, document, command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/documents/{document_id}/delete",
    response_model=CommandResultResponse,
    status_code=201,
)
def delete_text(
    document_id: str,
    request: DeleteRequest,
    session: Session = Depends(get_session),
) -> CommandResultResponse:
    document = _get_or_create_document(session, document_id)
    command = DeleteTextCommand(document, request.start, request.end)
    try:
        return _run_command(session, document_id, document, command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/documents/{document_id}/format",
    response_model=CommandResultResponse,
    status_code=201,
)
def format_text(
    document_id: str,
    request: FormatRequest,
    session: Session = Depends(get_session),
) -> CommandResultResponse:
    document = _get_or_create_document(session, document_id)
    command = FormatCommand(document, request.start, request.end, request.format_type)
    try:
        return _run_command(session, document_id, document, command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/documents/{document_id}/undo", response_model=CommandResultResponse)
def undo(
    document_id: str, session: Session = Depends(get_session)
) -> CommandResultResponse:
    document = _get_or_create_document(session, document_id)
    invoker = _get_invoker(document_id)
    result = invoker.undo()
    if result is None:
        raise HTTPException(status_code=409, detail="Nothing to undo")
    PostgresDocumentRepository(session).save(document)
    return CommandResultResponse(
        success=result.success,
        message=result.message,
        content_snapshot=result.content_snapshot,
    )


@app.post("/documents/{document_id}/redo", response_model=CommandResultResponse)
def redo(
    document_id: str, session: Session = Depends(get_session)
) -> CommandResultResponse:
    document = _get_or_create_document(session, document_id)
    invoker = _get_invoker(document_id)
    result = invoker.redo()
    if result is None:
        raise HTTPException(status_code=409, detail="Nothing to redo")
    PostgresDocumentRepository(session).save(document)
    return CommandResultResponse(
        success=result.success,
        message=result.message,
        content_snapshot=result.content_snapshot,
    )


@app.get("/documents/{document_id}/history")
def get_history(document_id: str) -> list[dict[str, object]]:
    invoker = _get_invoker(document_id)
    return [
        {
            "command_id": info.command_id,
            "description": info.description,
            "is_reversible": info.is_reversible,
            "executed_at": info.executed_at.isoformat(),
        }
        for info in invoker.get_history()
    ]
