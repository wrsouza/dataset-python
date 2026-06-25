"""FastAPI application entrypoint — composition root."""
from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from documents.application.use_cases import (
    CreateDocumentInput,
    CreateDocumentUseCase,
    EditDocumentInput,
    EditDocumentUseCase,
    GetHistoryUseCase,
    RestoreVersionUseCase,
    UndoDocumentUseCase,
)
from documents.domain.entities import (
    DocumentNotFoundError,
    NoHistoryError,
    VersionNotFoundError,
)
from documents.infrastructure.caretaker import PostgresVersionHistory
from documents.infrastructure.database import create_pool
from documents.infrastructure.repository import DocumentRepository
from documents.settings import Settings

settings = Settings()
_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _pool
    _pool = await create_pool(settings)
    repo = DocumentRepository(_pool)
    await repo.init_schema()
    yield
    await _pool.close()


app = FastAPI(title="Document Version History", lifespan=lifespan)


# ── Dependency injection ──────────────────────────────────────────────────────


def get_repository() -> DocumentRepository:
    assert _pool is not None
    return DocumentRepository(_pool)


def get_caretaker() -> PostgresVersionHistory:
    assert _pool is not None
    return PostgresVersionHistory(_pool)


# ── Request / Response schemas ────────────────────────────────────────────────


class CreateDocumentRequest(BaseModel):
    title: str
    content: str
    metadata: dict[str, Any] = {}
    author: str


class EditDocumentRequest(BaseModel):
    content: str
    metadata: dict[str, Any] = {}
    author: str


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    metadata: dict[str, Any]
    current_version: int


class VersionResponse(BaseModel):
    version: int
    author: str
    created_at: str
    content: str
    metadata: dict[str, Any]


# ── Routes ────────────────────────────────────────────────────────────────────


@app.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    body: CreateDocumentRequest,
    repo: DocumentRepository = Depends(get_repository),
    caretaker: PostgresVersionHistory = Depends(get_caretaker),
) -> DocumentResponse:
    use_case = CreateDocumentUseCase(repo, caretaker)
    doc = await use_case.execute(
        CreateDocumentInput(
            id=str(uuid.uuid4()),
            title=body.title,
            content=body.content,
            metadata=body.metadata,
            author=body.author,
        )
    )
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata,
        current_version=doc.current_version,
    )


@app.put("/documents/{document_id}", response_model=DocumentResponse)
async def edit_document(
    document_id: str,
    body: EditDocumentRequest,
    repo: DocumentRepository = Depends(get_repository),
    caretaker: PostgresVersionHistory = Depends(get_caretaker),
) -> DocumentResponse:
    use_case = EditDocumentUseCase(repo, caretaker)
    try:
        doc = await use_case.execute(
            EditDocumentInput(
                document_id=document_id,
                new_content=body.content,
                new_metadata=body.metadata,
                author=body.author,
            )
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata,
        current_version=doc.current_version,
    )


@app.post("/documents/{document_id}/restore/{version}", response_model=DocumentResponse)
async def restore_version(
    document_id: str,
    version: int,
    repo: DocumentRepository = Depends(get_repository),
    caretaker: PostgresVersionHistory = Depends(get_caretaker),
) -> DocumentResponse:
    use_case = RestoreVersionUseCase(repo, caretaker)
    try:
        doc = await use_case.execute(document_id, version)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except VersionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata,
        current_version=doc.current_version,
    )


@app.post("/documents/{document_id}/undo", response_model=DocumentResponse)
async def undo_document(
    document_id: str,
    repo: DocumentRepository = Depends(get_repository),
    caretaker: PostgresVersionHistory = Depends(get_caretaker),
) -> DocumentResponse:
    use_case = UndoDocumentUseCase(repo, caretaker)
    try:
        doc = await use_case.execute(document_id)
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NoHistoryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        content=doc.content,
        metadata=doc.metadata,
        current_version=doc.current_version,
    )


@app.get("/documents/{document_id}/history", response_model=list[VersionResponse])
async def get_history(
    document_id: str,
    caretaker: PostgresVersionHistory = Depends(get_caretaker),
) -> list[VersionResponse]:
    use_case = GetHistoryUseCase(caretaker)
    versions = await use_case.execute(document_id)
    return [
        VersionResponse(
            version=v.version,
            author=v.author,
            created_at=v.created_at.isoformat(),
            content=v.content,
            metadata=v.metadata,
        )
        for v in versions
    ]
