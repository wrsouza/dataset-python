"""Unit tests for the Auth Provider Factory Method pattern.

Key assertions:
- Each ConcreteCreator's create_provider() returns the matching ConcreteProduct.
- The abstract Creator's get_scheme_name() template behaviour works for all
  subclasses without needing to override it explicitly (except where it is).
- Each provider's authenticate / issue_token / validate_token / revoke cycle
  works for the documented "happy path" and raises domain exceptions for
  invalid input — including mocked-out OAuth providers (Google, GitHub).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from auth.domain.entities import (
    AuthenticationError,
    InvalidTokenError,
    UnsupportedSchemeError,
)
from auth.domain.interfaces import AuthProviderFactory
from auth.infrastructure.creators import (
    APIKeyAuthFactory,
    APIKeyAuthProvider,
    EmailPasswordAuthFactory,
    EmailPasswordAuthProvider,
    OAuthGithubAuthFactory,
    OAuthGithubAuthProvider,
    OAuthGoogleAuthFactory,
    OAuthGoogleAuthProvider,
    get_factory,
)

# ── Factory Method: Creator -> ConcreteProduct mapping ───────────────────────


@pytest.mark.parametrize(
    ("factory_cls", "provider_cls", "scheme_name"),
    [
        (EmailPasswordAuthFactory, EmailPasswordAuthProvider, "EmailPassword"),
        (OAuthGoogleAuthFactory, OAuthGoogleAuthProvider, "OAuthGoogle"),
        (OAuthGithubAuthFactory, OAuthGithubAuthProvider, "OAuthGithub"),
        (APIKeyAuthFactory, APIKeyAuthProvider, "APIKey"),
    ],
)
def test_concrete_creator_builds_matching_product(
    factory_cls: type[AuthProviderFactory],
    provider_cls: type,
    scheme_name: str,
) -> None:
    factory = factory_cls()
    provider = factory.create_provider()
    assert isinstance(provider, provider_cls)
    assert factory.get_scheme_name() == scheme_name


def test_creator_is_abstract() -> None:
    with pytest.raises(TypeError):
        AuthProviderFactory()  # type: ignore[abstract]


def test_default_get_scheme_name_strips_factory_suffix() -> None:
    """The base Creator provides a sensible default scheme name (template method)."""

    class CustomAuthFactory(AuthProviderFactory):
        def create_provider(self):  # type: ignore[no-untyped-def]
            return EmailPasswordAuthProvider()

    factory = CustomAuthFactory()
    assert factory.get_scheme_name() == "Custom"


# ── Registry lookups ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("scheme", "expected_cls"),
    [
        ("email_password", EmailPasswordAuthFactory),
        ("oauth_google", OAuthGoogleAuthFactory),
        ("oauth_github", OAuthGithubAuthFactory),
        ("api_key", APIKeyAuthFactory),
    ],
)
def test_get_factory_returns_registered_creator(
    scheme: str, expected_cls: type
) -> None:
    assert isinstance(get_factory(scheme), expected_cls)


def test_get_factory_raises_for_unknown_scheme() -> None:
    with pytest.raises(UnsupportedSchemeError):
        get_factory("unknown_scheme")


# ── EmailPasswordAuthProvider ─────────────────────────────────────────────────


def test_email_password_authenticate_success() -> None:
    provider = EmailPasswordAuthProvider()
    assert (
        provider.authenticate({"username": "alice", "password": "password123"})
        == "alice"
    )


def test_email_password_authenticate_invalid_password() -> None:
    provider = EmailPasswordAuthProvider()
    with pytest.raises(AuthenticationError):
        provider.authenticate({"username": "alice", "password": "wrong"})


def test_email_password_full_lifecycle() -> None:
    provider = EmailPasswordAuthProvider()
    user_id = provider.authenticate({"username": "bob", "password": "password123"})
    token = provider.issue_token(user_id)
    assert provider.validate_token(token) == user_id
    provider.revoke(token)
    with pytest.raises(InvalidTokenError):
        provider.validate_token(token)


def test_email_password_validate_unknown_token() -> None:
    provider = EmailPasswordAuthProvider()
    with pytest.raises(InvalidTokenError):
        provider.validate_token("not-a-real-token")


# ── OAuthGoogleAuthProvider (mocked external identity) ───────────────────────


def test_oauth_google_authenticate_success_with_mocked_directory() -> None:
    provider = OAuthGoogleAuthProvider()
    with patch.dict(
        "auth.infrastructure.creators.GOOGLE_ACCOUNTS",
        {"mocked-code": "mocked@gmail.com"},
        clear=True,
    ):
        assert provider.authenticate({"auth_code": "mocked-code"}) == "mocked@gmail.com"


def test_oauth_google_authenticate_invalid_code() -> None:
    provider = OAuthGoogleAuthProvider()
    with pytest.raises(AuthenticationError):
        provider.authenticate({"auth_code": "invalid-code"})


def test_oauth_google_full_lifecycle() -> None:
    provider = OAuthGoogleAuthProvider()
    user_id = provider.authenticate({"auth_code": "google-oauth-code-alice"})
    token = provider.issue_token(user_id)
    assert provider.validate_token(token) == user_id
    provider.revoke(token)
    with pytest.raises(InvalidTokenError):
        provider.validate_token(token)


# ── OAuthGithubAuthProvider (mocked external identity) ───────────────────────


def test_oauth_github_authenticate_success_with_mocked_directory() -> None:
    provider = OAuthGithubAuthProvider()
    with patch.dict(
        "auth.infrastructure.creators.GITHUB_ACCOUNTS",
        {"mocked-code": "mocked-gh"},
        clear=True,
    ):
        assert provider.authenticate({"auth_code": "mocked-code"}) == "mocked-gh"


def test_oauth_github_authenticate_invalid_code() -> None:
    provider = OAuthGithubAuthProvider()
    with pytest.raises(AuthenticationError):
        provider.authenticate({"auth_code": "invalid-code"})


def test_oauth_github_full_lifecycle() -> None:
    provider = OAuthGithubAuthProvider()
    user_id = provider.authenticate({"auth_code": "github-oauth-code-bob"})
    token = provider.issue_token(user_id)
    assert provider.validate_token(token) == user_id
    provider.revoke(token)
    with pytest.raises(InvalidTokenError):
        provider.validate_token(token)


# ── APIKeyAuthProvider ─────────────────────────────────────────────────────────


def test_api_key_authenticate_success() -> None:
    provider = APIKeyAuthProvider({"ak_test": "carol"})
    assert provider.authenticate({"api_key": "ak_test"}) == "carol"


def test_api_key_authenticate_invalid_key() -> None:
    provider = APIKeyAuthProvider({"ak_test": "carol"})
    with pytest.raises(AuthenticationError):
        provider.authenticate({"api_key": "unknown-key"})


def test_api_key_issue_token_returns_existing_key() -> None:
    provider = APIKeyAuthProvider({"ak_test": "carol"})
    assert provider.issue_token("carol") == "ak_test"


def test_api_key_issue_token_generates_new_key_when_absent() -> None:
    provider = APIKeyAuthProvider({})
    token = provider.issue_token("dave")
    assert token.startswith("ak_dave_")
    assert provider.validate_token(token) == "dave"


def test_api_key_revoke_blocks_future_validation() -> None:
    provider = APIKeyAuthProvider({"ak_test": "carol"})
    provider.revoke("ak_test")
    with pytest.raises(InvalidTokenError):
        provider.validate_token("ak_test")
