"""Authenticator context — uses AuthenticationStrategy via composition,
swappable at runtime."""

from __future__ import annotations

from typing import Any

from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.interfaces import AuthenticationStrategy


class NoStrategyConfiguredError(Exception):
    def __init__(self) -> None:
        super().__init__("No authentication strategy configured")


class Authenticator:
    """Context that delegates authentication to a pluggable
    AuthenticationStrategy.

    DIP: depends on AuthenticationStrategy ABC, not concrete implementations.
    """

    def __init__(self, strategy: AuthenticationStrategy | None = None) -> None:
        self._strategy: AuthenticationStrategy | None = strategy

    def set_strategy(self, strategy: AuthenticationStrategy) -> None:
        self._strategy = strategy

    @property
    def current_strategy(self) -> AuthenticationStrategy | None:
        return self._strategy

    def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        """Delegate authentication to the configured strategy.

        Raises:
            NoStrategyConfiguredError: when no strategy has been set.
        """
        if self._strategy is None:
            raise NoStrategyConfiguredError()
        return self._strategy.authenticate(credentials)
