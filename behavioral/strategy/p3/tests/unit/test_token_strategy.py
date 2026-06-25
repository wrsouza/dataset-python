"""Unit tests for TokenAuthStrategy, against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from auth_strategy.django_app.models import ApiTokenModel
from auth_strategy.infrastructure.strategies.token import TokenAuthStrategy

pytestmark = pytest.mark.django_db


def test_authenticate_succeeds_with_active_token() -> None:
    ApiTokenModel.objects.create(token="abc123", user_id="u1", is_active=True)
    strategy = TokenAuthStrategy()

    result = strategy.authenticate({"token": "abc123"})

    assert result.success is True
    assert result.user_id == "u1"


def test_authenticate_fails_with_unknown_token() -> None:
    strategy = TokenAuthStrategy()

    result = strategy.authenticate({"token": "does-not-exist"})

    assert result.success is False
    assert result.reason == "invalid token"


def test_authenticate_fails_with_revoked_token() -> None:
    ApiTokenModel.objects.create(token="abc123", user_id="u1", is_active=False)
    strategy = TokenAuthStrategy()

    result = strategy.authenticate({"token": "abc123"})

    assert result.success is False
    assert result.reason == "token revoked"
