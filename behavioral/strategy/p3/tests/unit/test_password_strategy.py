"""Unit tests for PasswordAuthStrategy, against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest
from django.contrib.auth.hashers import make_password

from auth_strategy.django_app.models import UserCredentialModel
from auth_strategy.infrastructure.strategies.password import PasswordAuthStrategy

pytestmark = pytest.mark.django_db


def _create_user(username: str, password: str, user_id: str) -> None:
    UserCredentialModel.objects.create(
        username=username, password_hash=make_password(password), user_id=user_id
    )


def test_authenticate_succeeds_with_correct_password() -> None:
    _create_user("ana", "s3cret", "u1")
    strategy = PasswordAuthStrategy()

    result = strategy.authenticate({"username": "ana", "password": "s3cret"})

    assert result.success is True
    assert result.user_id == "u1"


def test_authenticate_fails_with_wrong_password() -> None:
    _create_user("ana", "s3cret", "u1")
    strategy = PasswordAuthStrategy()

    result = strategy.authenticate({"username": "ana", "password": "wrong"})

    assert result.success is False
    assert result.reason == "invalid password"


def test_authenticate_fails_for_unknown_username() -> None:
    strategy = PasswordAuthStrategy()

    result = strategy.authenticate({"username": "unknown", "password": "x"})

    assert result.success is False
    assert result.reason == "user not found"
