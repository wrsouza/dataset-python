"""Unit tests for domain entities (no framework dependency)."""

from __future__ import annotations

from permission_layers.domain.entities import (
    ANONYMOUS_USER,
    AccessAction,
    AccessDeniedError,
    Resource,
    ResourceAccessResult,
    User,
)


def test_user_has_role_true() -> None:
    user = User(user_id="u1", username="alice", roles=frozenset({"editor"}))
    assert user.has_role("editor") is True


def test_user_has_role_false() -> None:
    user = User(user_id="u1", username="alice", roles=frozenset({"viewer"}))
    assert user.has_role("editor") is False


def test_anonymous_user_is_not_authenticated() -> None:
    assert ANONYMOUS_USER.is_authenticated is False


def test_result_with_layer_prepends_layer_name() -> None:
    result = ResourceAccessResult(
        granted=True, reason="ok", resource_id="r1", user_id="u1"
    )
    updated = result.with_layer("audit_log")
    assert updated.layers_applied == ("audit_log",)
    assert updated.granted is True


def test_result_denied_by_flips_granted_and_records_reason() -> None:
    result = ResourceAccessResult(
        granted=True, reason="ok", resource_id="r1", user_id="u1"
    )
    denied = result.denied_by("require_role", "missing role")
    assert denied.granted is False
    assert denied.reason == "missing role"
    assert denied.layers_applied == ("require_role",)


def test_access_denied_error_message() -> None:
    error = AccessDeniedError("missing role")
    assert "missing role" in str(error)


def test_resource_is_frozen_dataclass() -> None:
    resource = Resource(resource_id="r1", owner_id="u1", title="Doc")
    assert resource.resource_id == "r1"


def test_access_action_values() -> None:
    assert AccessAction.READ.value == "read"
    assert AccessAction.WRITE.value == "write"
    assert AccessAction.DELETE.value == "delete"
