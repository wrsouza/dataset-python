"""Application use cases for authentication — depend only on abstractions (DIP)."""

from __future__ import annotations

from typing import Any

from auth.domain.entities import AuthResult
from auth.domain.interfaces import AuthProviderFactory


class LoginUseCase:
    """Authenticate a user and return an auth token."""

    def __init__(self, factory: AuthProviderFactory) -> None:
        self._factory = factory

    def execute(self, credentials: dict[str, Any]) -> AuthResult:
        provider = self._factory.create_provider()
        user_id = provider.authenticate(credentials)
        token = provider.issue_token(user_id)
        return AuthResult(
            user_id=user_id,
            scheme=self._factory.get_scheme_name(),
            token=token,
        )


class ValidateTokenUseCase:
    """Validate a token and return the associated user ID."""

    def __init__(self, factory: AuthProviderFactory) -> None:
        self._factory = factory

    def execute(self, token: str) -> str:
        provider = self._factory.create_provider()
        return provider.validate_token(token)


class LogoutUseCase:
    """Revoke a token, effectively logging out the user."""

    def __init__(self, factory: AuthProviderFactory) -> None:
        self._factory = factory

    def execute(self, token: str) -> None:
        provider = self._factory.create_provider()
        provider.revoke(token)
