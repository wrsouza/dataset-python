"""Django views — Client of the Access Control subsystem.

Views depend on `request.document_service` (a DocumentService — either the
PermissionProxy or, in theory, the bare RealSubject) injected by
PermissionProxyMiddleware. They never construct either themselves.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from django.http import Http404, HttpRequest, HttpResponse
from django.views import View

from access_control.application.use_cases import (
    CreateDocumentUseCase,
    DeleteDocumentUseCase,
    GetDocumentUseCase,
    ListDocumentsUseCase,
    UpdateDocumentUseCase,
)
from access_control.domain.entities import Document
from access_control.domain.exceptions import (
    DocumentNotFoundError,
    InactiveUserError,
    PermissionDeniedError,
)

if TYPE_CHECKING:
    from access_control.domain.interfaces import DocumentService


class _AuthorizedRequest(HttpRequest):
    """Typing helper: the request after PermissionProxyMiddleware has run."""

    document_service: DocumentService


def _serialize(document: Document) -> dict[str, object]:
    return {
        "doc_id": document.doc_id,
        "title": document.title,
        "content": document.content,
        "owner_id": document.owner_id,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
    }


def _json(data: object, status: int = 200) -> HttpResponse:
    return HttpResponse(
        json.dumps(data), content_type="application/json", status=status
    )


def _forbidden(exc: Exception) -> HttpResponse:
    return _json({"error": str(exc)}, status=403)


class DocumentListCreateView(View):
    """GET /documents/ — list; POST /documents/ — create."""

    def get(self, request: _AuthorizedRequest) -> HttpResponse:
        use_case = ListDocumentsUseCase(service=request.document_service)
        try:
            documents = use_case.execute({})
        except PermissionDeniedError as exc:
            return _forbidden(exc)
        except InactiveUserError as exc:
            return _forbidden(exc)
        return _json([_serialize(doc) for doc in documents])

    def post(self, request: _AuthorizedRequest) -> HttpResponse:
        data = json.loads(request.body)
        use_case = CreateDocumentUseCase(service=request.document_service)
        try:
            document = use_case.execute(data)
        except PermissionDeniedError as exc:
            return _forbidden(exc)
        except InactiveUserError as exc:
            return _forbidden(exc)
        return _json(_serialize(document), status=201)


class DocumentDetailView(View):
    """GET/PUT/DELETE /documents/<doc_id>/."""

    def get(self, request: _AuthorizedRequest, doc_id: str) -> HttpResponse:
        use_case = GetDocumentUseCase(service=request.document_service)
        try:
            document = use_case.execute(doc_id)
        except DocumentNotFoundError as exc:
            raise Http404(str(exc)) from exc
        except (PermissionDeniedError, InactiveUserError) as exc:
            return _forbidden(exc)
        return _json(_serialize(document))

    def put(self, request: _AuthorizedRequest, doc_id: str) -> HttpResponse:
        data = json.loads(request.body)
        use_case = UpdateDocumentUseCase(service=request.document_service)
        try:
            document = use_case.execute(doc_id, data)
        except DocumentNotFoundError as exc:
            raise Http404(str(exc)) from exc
        except (PermissionDeniedError, InactiveUserError) as exc:
            return _forbidden(exc)
        return _json(_serialize(document))

    def delete(self, request: _AuthorizedRequest, doc_id: str) -> HttpResponse:
        use_case = DeleteDocumentUseCase(service=request.document_service)
        try:
            use_case.execute(doc_id)
        except DocumentNotFoundError as exc:
            raise Http404(str(exc)) from exc
        except (PermissionDeniedError, InactiveUserError) as exc:
            return _forbidden(exc)
        return _json({"deleted": doc_id})
