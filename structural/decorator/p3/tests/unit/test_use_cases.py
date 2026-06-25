"""Unit tests for EvaluateDocumentAccessUseCase — composition logic."""

from __future__ import annotations

from permission_layers.application.use_cases import (
    EvaluateAccessRequest,
    EvaluateDocumentAccessUseCase,
)
from permission_layers.domain.entities import AccessAction, Resource, User
from permission_layers.infrastructure.repository import InMemoryResourceRepository

DOCUMENT = Resource(resource_id="doc-1", owner_id="owner-1", title="Plan")


def _repository() -> InMemoryResourceRepository:
    return InMemoryResourceRepository({DOCUMENT.resource_id: DOCUMENT})


def test_read_action_does_not_require_ownership() -> None:
    use_case = EvaluateDocumentAccessUseCase(_repository())
    stranger = User(user_id="stranger", username="s", is_authenticated=True)
    request = EvaluateAccessRequest(
        user=stranger,
        resource_id=DOCUMENT.resource_id,
        owner_id=DOCUMENT.owner_id,
        title=DOCUMENT.title,
        action=AccessAction.READ,
        required_role=None,
    )
    result = use_case.execute(request)
    assert result.granted is True
    assert "require_ownership" not in result.layers_applied


def test_write_action_requires_ownership() -> None:
    use_case = EvaluateDocumentAccessUseCase(_repository())
    stranger = User(user_id="stranger", username="s", is_authenticated=True)
    request = EvaluateAccessRequest(
        user=stranger,
        resource_id=DOCUMENT.resource_id,
        owner_id=DOCUMENT.owner_id,
        title=DOCUMENT.title,
        action=AccessAction.WRITE,
        required_role=None,
    )
    result = use_case.execute(request)
    assert result.granted is False
    assert "require_ownership" in result.layers_applied


def test_required_role_adds_role_layer() -> None:
    use_case = EvaluateDocumentAccessUseCase(_repository())
    user = User(
        user_id="owner-1", username="owner", roles=frozenset(), is_authenticated=True
    )
    request = EvaluateAccessRequest(
        user=user,
        resource_id=DOCUMENT.resource_id,
        owner_id=DOCUMENT.owner_id,
        title=DOCUMENT.title,
        action=AccessAction.READ,
        required_role="admin",
    )
    result = use_case.execute(request)
    assert result.granted is False
    assert "require_role" in result.layers_applied


def test_anonymous_user_always_denied() -> None:
    use_case = EvaluateDocumentAccessUseCase(_repository())
    anonymous = User(user_id="", username="anon", is_authenticated=False)
    request = EvaluateAccessRequest(
        user=anonymous,
        resource_id=DOCUMENT.resource_id,
        owner_id=DOCUMENT.owner_id,
        title=DOCUMENT.title,
        action=AccessAction.READ,
        required_role=None,
    )
    result = use_case.execute(request)
    assert result.granted is False
    assert "require_auth" in result.layers_applied


def test_audit_log_always_outermost_layer() -> None:
    use_case = EvaluateDocumentAccessUseCase(_repository())
    user = User(user_id="owner-1", username="owner", is_authenticated=True)
    request = EvaluateAccessRequest(
        user=user,
        resource_id=DOCUMENT.resource_id,
        owner_id=DOCUMENT.owner_id,
        title=DOCUMENT.title,
        action=AccessAction.READ,
        required_role=None,
    )
    result = use_case.execute(request)
    assert result.layers_applied[0] == "audit_log"
