"""ConcreteCreators and ConcreteProducts for each auth scheme.

EmailPasswordAuthFactory -> EmailPasswordAuthProvider
OAuthGoogleAuthFactory   -> OAuthGoogleAuthProvider
OAuthGithubAuthFactory   -> OAuthGithubAuthProvider
APIKeyAuthFactory        -> APIKeyAuthProvider

All implementations are self-contained and simulate the external service
(no real network calls to Google/GitHub) — this keeps the example focused
on the Factory Method pattern rather than OAuth wire protocols.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import Any

from auth.domain.entities import AuthenticationError, InvalidTokenError
from auth.domain.interfaces import AuthProvider, AuthProviderFactory

# Simulated local user store (replaces a real DB for this example).
USERS: dict[str, str] = {
    "alice": "hashed_pass_alice",
    "bob": "hashed_pass_bob",
    "admin": "hashed_pass_admin",
}

# Simulated OAuth identity providers — pretend "social login" directories.
GOOGLE_ACCOUNTS: dict[str, str] = {
    "google-oauth-code-alice": "alice@gmail.com",
    "google-oauth-code-bob": "bob@gmail.com",
}
GITHUB_ACCOUNTS: dict[str, str] = {
    "github-oauth-code-alice": "alice-gh",
    "github-oauth-code-bob": "bob-gh",
}

# Simulated API key store {key: user_id}.
API_KEYS: dict[str, str] = {
    "ak_alice_test_key_001": "alice",
    "ak_bob_test_key_002": "bob",
}


def _check_password(username: str, password: str) -> bool:
    """Mock password verification — always accepts 'password123' for any user."""
    return password == "password123" and username in USERS


def _generate_opaque_token(user_id: str, scheme: str) -> str:
    """Build a deterministic-looking opaque token for the given user/scheme."""
    nonce = secrets.token_hex(8)
    raw = f"{scheme}:{user_id}:{nonce}:{time.time()}"
    return hashlib.sha256(raw.encode()).hexdigest()


# ── Email/Password ──────────────────────────────────────────────────────────


class EmailPasswordAuthProvider:
    """ConcreteProduct — classic username/password authentication.

    Session and revocation state are kept at class level (shared by every
    instance) so that a token issued by one ``create_provider()`` call can
    still be validated/revoked by a later call — in production this state
    would live in a database or cache instead.
    """

    _sessions: dict[str, str] = {}
    _revoked: set[str] = set()

    def authenticate(self, credentials: dict[str, Any]) -> str:
        username = str(credentials.get("username", ""))
        password = str(credentials.get("password", ""))
        if not _check_password(username, password):
            raise AuthenticationError("Invalid username or password")
        return username

    def issue_token(self, user_id: str) -> str:
        token = _generate_opaque_token(user_id, "email-password")
        self._sessions[token] = user_id
        return token

    def validate_token(self, token: str) -> str:
        if token in self._revoked or token not in self._sessions:
            raise InvalidTokenError("Unknown or revoked token")
        return self._sessions[token]

    def revoke(self, token: str) -> None:
        self._revoked.add(token)


class EmailPasswordAuthFactory(AuthProviderFactory):
    """ConcreteCreator — creates an EmailPasswordAuthProvider."""

    def create_provider(self) -> AuthProvider:
        return EmailPasswordAuthProvider()

    def get_scheme_name(self) -> str:
        return "EmailPassword"


# ── OAuth Google (simulated) ────────────────────────────────────────────────


class OAuthGoogleAuthProvider:
    """ConcreteProduct — simulates a Google OAuth2 authorization-code exchange.

    No real HTTP call is made: ``GOOGLE_ACCOUNTS`` plays the role of Google's
    identity directory for this educational example. Session state is kept
    at class level so tokens survive across `create_provider()` calls.
    """

    _sessions: dict[str, str] = {}
    _revoked: set[str] = set()

    def authenticate(self, credentials: dict[str, Any]) -> str:
        auth_code = credentials.get("auth_code", "")
        email = GOOGLE_ACCOUNTS.get(auth_code)
        if email is None:
            raise AuthenticationError("Invalid Google authorization code")
        return email

    def issue_token(self, user_id: str) -> str:
        token = _generate_opaque_token(user_id, "oauth-google")
        self._sessions[token] = user_id
        return token

    def validate_token(self, token: str) -> str:
        if token in self._revoked or token not in self._sessions:
            raise InvalidTokenError("Unknown or revoked Google token")
        return self._sessions[token]

    def revoke(self, token: str) -> None:
        self._revoked.add(token)


class OAuthGoogleAuthFactory(AuthProviderFactory):
    """ConcreteCreator — creates an OAuthGoogleAuthProvider."""

    def create_provider(self) -> AuthProvider:
        return OAuthGoogleAuthProvider()

    def get_scheme_name(self) -> str:
        return "OAuthGoogle"


# ── OAuth GitHub (simulated) ────────────────────────────────────────────────


class OAuthGithubAuthProvider:
    """ConcreteProduct — simulates a GitHub OAuth2 authorization-code exchange.

    No real HTTP call is made: ``GITHUB_ACCOUNTS`` plays the role of GitHub's
    identity directory for this educational example. Session state is kept
    at class level so tokens survive across `create_provider()` calls.
    """

    _sessions: dict[str, str] = {}
    _revoked: set[str] = set()

    def authenticate(self, credentials: dict[str, Any]) -> str:
        auth_code = credentials.get("auth_code", "")
        login = GITHUB_ACCOUNTS.get(auth_code)
        if login is None:
            raise AuthenticationError("Invalid GitHub authorization code")
        return login

    def issue_token(self, user_id: str) -> str:
        token = _generate_opaque_token(user_id, "oauth-github")
        self._sessions[token] = user_id
        return token

    def validate_token(self, token: str) -> str:
        if token in self._revoked or token not in self._sessions:
            raise InvalidTokenError("Unknown or revoked GitHub token")
        return self._sessions[token]

    def revoke(self, token: str) -> None:
        self._revoked.add(token)


class OAuthGithubAuthFactory(AuthProviderFactory):
    """ConcreteCreator — creates an OAuthGithubAuthProvider."""

    def create_provider(self) -> AuthProvider:
        return OAuthGithubAuthProvider()

    def get_scheme_name(self) -> str:
        return "OAuthGithub"


# ── API Key ──────────────────────────────────────────────────────────────────


class APIKeyAuthProvider:
    """ConcreteProduct — static API key authentication."""

    def __init__(self, key_store: dict[str, str] | None = None) -> None:
        self._keys = key_store if key_store is not None else API_KEYS
        self._revoked: set[str] = set()

    def authenticate(self, credentials: dict[str, Any]) -> str:
        api_key = credentials.get("api_key", "")
        if api_key in self._revoked or api_key not in self._keys:
            raise AuthenticationError("Invalid API key")
        return self._keys[api_key]

    def issue_token(self, user_id: str) -> str:
        for key, uid in self._keys.items():
            if uid == user_id and key not in self._revoked:
                return key
        new_key = f"ak_{user_id}_{secrets.token_hex(8)}"
        self._keys[new_key] = user_id
        return new_key

    def validate_token(self, token: str) -> str:
        if token in self._revoked or token not in self._keys:
            raise InvalidTokenError("Invalid or revoked API key")
        return self._keys[token]

    def revoke(self, token: str) -> None:
        self._revoked.add(token)


class APIKeyAuthFactory(AuthProviderFactory):
    """ConcreteCreator — creates an APIKeyAuthProvider."""

    def create_provider(self) -> AuthProvider:
        return APIKeyAuthProvider()

    def get_scheme_name(self) -> str:
        return "APIKey"


# ── Registry ─────────────────────────────────────────────────────────────────

SCHEME_REGISTRY: dict[str, AuthProviderFactory] = {
    "email_password": EmailPasswordAuthFactory(),
    "oauth_google": OAuthGoogleAuthFactory(),
    "oauth_github": OAuthGithubAuthFactory(),
    "api_key": APIKeyAuthFactory(),
}


def get_factory(scheme: str) -> AuthProviderFactory:
    """Look up the ConcreteCreator registered for the given scheme name."""
    factory = SCHEME_REGISTRY.get(scheme)
    if factory is None:
        from auth.domain.entities import UnsupportedSchemeError

        raise UnsupportedSchemeError(scheme)
    return factory


__all__ = [
    "API_KEYS",
    "GITHUB_ACCOUNTS",
    "GOOGLE_ACCOUNTS",
    "USERS",
    "SCHEME_REGISTRY",
    "APIKeyAuthFactory",
    "APIKeyAuthProvider",
    "EmailPasswordAuthFactory",
    "EmailPasswordAuthProvider",
    "OAuthGithubAuthFactory",
    "OAuthGithubAuthProvider",
    "OAuthGoogleAuthFactory",
    "OAuthGoogleAuthProvider",
    "get_factory",
]
