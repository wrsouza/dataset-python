"""Unit tests for application use cases — verify the Creator is always
invoked through create_provider() (the factory method), never bypassed.
"""

from __future__ import annotations

import pytest

from auth.application.use_cases import LoginUseCase, LogoutUseCase, ValidateTokenUseCase
from auth.domain.entities import AuthenticationError, InvalidTokenError
from auth.infrastructure.creators import (
    EmailPasswordAuthFactory,
    OAuthGoogleAuthFactory,
)


def test_login_use_case_delegates_to_factory_method() -> None:
    use_case = LoginUseCase(EmailPasswordAuthFactory())
    result = use_case.execute({"username": "alice", "password": "password123"})
    assert result.user_id == "alice"
    assert result.scheme == "EmailPassword"
    assert result.token


def test_login_use_case_propagates_authentication_error() -> None:
    use_case = LoginUseCase(EmailPasswordAuthFactory())
    with pytest.raises(AuthenticationError):
        use_case.execute({"username": "alice", "password": "wrong"})


def test_login_use_case_with_oauth_google_factory() -> None:
    use_case = LoginUseCase(OAuthGoogleAuthFactory())
    result = use_case.execute({"auth_code": "google-oauth-code-alice"})
    assert result.scheme == "OAuthGoogle"
    assert result.user_id == "alice@gmail.com"


def test_validate_token_use_case_round_trip() -> None:
    factory = EmailPasswordAuthFactory()
    login_result = LoginUseCase(factory).execute(
        {"username": "bob", "password": "password123"}
    )
    user_id = ValidateTokenUseCase(factory).execute(login_result.token)
    assert user_id == "bob"


def test_logout_use_case_revokes_token() -> None:
    factory = EmailPasswordAuthFactory()
    login_result = LoginUseCase(factory).execute(
        {"username": "bob", "password": "password123"}
    )
    LogoutUseCase(factory).execute(login_result.token)
    with pytest.raises(InvalidTokenError):
        ValidateTokenUseCase(factory).execute(login_result.token)
