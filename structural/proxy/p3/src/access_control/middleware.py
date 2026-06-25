"""Middleware: resolves the current user and injects a PermissionProxy.

Views never construct DjangoDocumentService or PermissionProxy themselves —
this is the composition root for every request. Client code (views) only
ever sees `request.document_service: DocumentService`.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from access_control.domain.entities import Role, User
from access_control.infrastructure.audit_logger import DjangoAuditLogger
from access_control.infrastructure.models import UserModel
from access_control.infrastructure.proxy import PermissionProxy
from access_control.infrastructure.real_subject import DjangoDocumentService


def _resolve_user(request: HttpRequest) -> User:
    """Look up the user identified by X-User-Id, defaulting to an inactive guest."""
    user_id = request.headers.get("X-User-Id", "anonymous")
    try:
        model = UserModel.objects.get(user_id=user_id)
    except UserModel.DoesNotExist:
        return User(user_id=user_id, username="anonymous", email="", role=Role.GUEST)
    return User(
        user_id=model.user_id,
        username=model.username,
        email=model.email,
        role=Role(model.role),
        is_active=model.is_active,
    )


class PermissionProxyMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user = _resolve_user(request)
        real_service = DjangoDocumentService()
        request.document_service = PermissionProxy(  # type: ignore[attr-defined]
            real_service=real_service, user=user, audit_logger=DjangoAuditLogger()
        )
        return self.get_response(request)
