"""Use cases — compose permission decorator layers around the base service.

Use cases depend only on `ResourceAccessService` (the Component
abstraction) and on `ResourceRepository`; neither is a concrete Django or
PostgreSQL type, so these use cases are fully testable with in-memory
fakes (Dependency Inversion).
"""

from __future__ import annotations

from dataclasses import dataclass

from permission_layers.domain.entities import (
    AccessAction,
    RequestContext,
    Resource,
    ResourceAccessResult,
    User,
)
from permission_layers.domain.interfaces import ResourceAccessService
from permission_layers.infrastructure.base_service import DocumentAccessService
from permission_layers.infrastructure.decorators import (
    AuditLogDecorator,
    RequireAuthDecorator,
    RequireOwnershipDecorator,
    RequireRoleDecorator,
)
from permission_layers.infrastructure.repository import ResourceRepository


@dataclass(frozen=True)
class EvaluateAccessRequest:
    """Input for `EvaluateDocumentAccessUseCase`."""

    user: User
    resource_id: str
    owner_id: str
    title: str
    action: AccessAction
    required_role: str | None


class EvaluateDocumentAccessUseCase:
    """Builds the decorator stack appropriate for the request and runs it.

    The exact layers applied depend on the request (e.g. ownership is only
    enforced for write/delete actions), which demonstrates that the same
    set of decorator classes can be recombined per call-site without
    touching the decorators themselves (Open/Closed).
    """

    def __init__(self, repository: ResourceRepository) -> None:
        self._repository = repository

    def execute(self, request: EvaluateAccessRequest) -> ResourceAccessResult:
        context = RequestContext(
            user=request.user,
            resource=Resource(
                resource_id=request.resource_id,
                owner_id=request.owner_id,
                title=request.title,
            ),
            action=request.action,
            required_role=request.required_role,
        )
        service = self._build_service(request)
        return service.access(context)

    def _build_service(self, request: EvaluateAccessRequest) -> ResourceAccessService:
        """Stack layers: auth -> role -> ownership (write/delete) -> audit."""
        service: ResourceAccessService = DocumentAccessService(self._repository)
        service = RequireAuthDecorator(service)
        if request.required_role is not None:
            service = RequireRoleDecorator(service, request.required_role)
        if request.action in (AccessAction.WRITE, AccessAction.DELETE):
            service = RequireOwnershipDecorator(service)
        return AuditLogDecorator(service)
