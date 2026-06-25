"""Unit tests for domain entities — pure Python, no Django/DB required."""

from __future__ import annotations

from access_control.domain.entities import Role, User


def test_role_ordering_values() -> None:
    assert {r.value for r in Role} == {"GUEST", "VIEWER", "EDITOR", "OWNER"}


def test_user_defaults_to_active() -> None:
    user = User(user_id="u1", username="alice", email="a@example.com", role=Role.OWNER)

    assert user.is_active is True
