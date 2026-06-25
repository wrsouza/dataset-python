"""Unit tests for the concrete permission decorators.

No Django/PostgreSQL involved — uses an in-memory repository and plain
dataclasses, exercising the decorators in full isolation.
"""

from __future__ import annotations

from permission_layers.domain.entities import (
    AccessAction,
    RequestContext,
    Resource,
    User,
)
from permission_layers.infrastructure.base_service import DocumentAccessService
from permission_layers.infrastructure.decorators import (
    AuditLogDecorator,
    RequireAuthDecorator,
    RequireOwnershipDecorator,
    RequireRoleDecorator,
)
from permission_layers.infrastructure.repository import InMemoryResourceRepository

OWNER = User(user_id="u1", username="alice", roles=frozenset({"editor"}))
OTHER_USER = User(user_id="u2", username="bob", roles=frozenset())
ANONYMOUS = User(user_id="", username="anon", is_authenticated=False)
DOCUMENT = Resource(resource_id="doc-1", owner_id="u1", title="Q3 Report")


def _repository() -> InMemoryResourceRepository:
    return InMemoryResourceRepository({DOCUMENT.resource_id: DOCUMENT})


def _context(user: User, action: AccessAction = AccessAction.READ) -> RequestContext:
    return RequestContext(user=user, resource=DOCUMENT, action=action)


def test_base_service_grants_when_resource_exists() -> None:
    service = DocumentAccessService(_repository())
    result = service.access(_context(OWNER))
    assert result.granted is True
    assert result.layers_applied == ("base_service",)


def test_base_service_denies_when_resource_missing() -> None:
    service = DocumentAccessService(InMemoryResourceRepository())
    result = service.access(_context(OWNER))
    assert result.granted is False
    assert "not found" in result.reason


def test_require_auth_denies_anonymous_user() -> None:
    service = RequireAuthDecorator(DocumentAccessService(_repository()))
    result = service.access(_context(ANONYMOUS))
    assert result.granted is False
    assert "not authenticated" in result.reason


def test_require_auth_allows_authenticated_user() -> None:
    service = RequireAuthDecorator(DocumentAccessService(_repository()))
    result = service.access(_context(OWNER))
    assert result.granted is True
    assert "require_auth" in result.layers_applied


def test_require_role_denies_user_without_role() -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = RequireRoleDecorator(base, required_role="admin")
    result = service.access(_context(OWNER))
    assert result.granted is False
    assert "lacks required role" in result.reason


def test_require_role_allows_user_with_role() -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = RequireRoleDecorator(base, required_role="editor")
    result = service.access(_context(OWNER))
    assert result.granted is True


def test_require_ownership_denies_non_owner() -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = RequireOwnershipDecorator(base)
    result = service.access(_context(OTHER_USER))
    assert result.granted is False
    assert "does not own" in result.reason


def test_require_ownership_allows_owner() -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = RequireOwnershipDecorator(base)
    result = service.access(_context(OWNER))
    assert result.granted is True


def test_short_circuit_stops_at_first_denial_layer() -> None:
    """Ownership check must not run (or matter) once auth already denied."""
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = RequireOwnershipDecorator(base)
    result = service.access(_context(ANONYMOUS))
    assert result.granted is False
    assert "not authenticated" in result.reason


def test_audit_log_records_layer_without_changing_outcome(caplog: object) -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = AuditLogDecorator(base)
    result = service.access(_context(OWNER))
    assert result.granted is True
    assert result.layers_applied[0] == "audit_log"


def test_audit_log_logs_denied_attempts(caplog: object) -> None:
    base = RequireAuthDecorator(DocumentAccessService(_repository()))
    service = AuditLogDecorator(base)
    result = service.access(_context(ANONYMOUS))
    assert result.granted is False


def test_full_stack_grants_owner_with_role_for_write() -> None:
    service = AuditLogDecorator(
        RequireOwnershipDecorator(
            RequireRoleDecorator(
                RequireAuthDecorator(DocumentAccessService(_repository())),
                required_role="editor",
            )
        )
    )
    result = service.access(_context(OWNER, action=AccessAction.WRITE))
    assert result.granted is True
    assert result.layers_applied == (
        "audit_log",
        "require_ownership",
        "require_role",
        "require_auth",
        "base_service",
    )


def test_full_stack_denies_non_owner_with_role_for_write() -> None:
    other_with_role = User(user_id="u2", username="bob", roles=frozenset({"editor"}))
    service = AuditLogDecorator(
        RequireOwnershipDecorator(
            RequireRoleDecorator(
                RequireAuthDecorator(DocumentAccessService(_repository())),
                required_role="editor",
            )
        )
    )
    result = service.access(_context(other_with_role, action=AccessAction.WRITE))
    assert result.granted is False
    assert "does not own" in result.reason


def test_layers_can_be_reordered_freely() -> None:
    """Decorators only depend on the Component abstraction, any order composes."""
    service_a = RequireOwnershipDecorator(
        RequireAuthDecorator(DocumentAccessService(_repository()))
    )
    service_b = RequireAuthDecorator(
        RequireOwnershipDecorator(DocumentAccessService(_repository()))
    )
    result_a = service_a.access(_context(OWNER))
    result_b = service_b.access(_context(OWNER))
    assert result_a.granted is True
    assert result_b.granted is True
