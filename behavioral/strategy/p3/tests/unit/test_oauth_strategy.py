"""Unit tests for OAuthStrategy, against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from auth_strategy.django_app.models import OAuthIdentityModel
from auth_strategy.infrastructure.strategies.oauth import OAuthStrategy

pytestmark = pytest.mark.django_db


def test_authenticate_succeeds_for_linked_identity() -> None:
    OAuthIdentityModel.objects.create(
        provider="google", provider_user_id="g-1", user_id="u1"
    )
    strategy = OAuthStrategy()

    result = strategy.authenticate({"provider": "google", "provider_user_id": "g-1"})

    assert result.success is True
    assert result.user_id == "u1"


def test_authenticate_fails_for_unlinked_identity() -> None:
    strategy = OAuthStrategy()

    result = strategy.authenticate(
        {"provider": "google", "provider_user_id": "unknown"}
    )

    assert result.success is False
    assert "no linked account" in (result.reason or "")
