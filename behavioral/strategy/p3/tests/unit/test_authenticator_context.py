"""Unit tests for the Authenticator context."""

from __future__ import annotations

import pytest

from auth_strategy.application.context import Authenticator, NoStrategyConfiguredError
from auth_strategy.domain.entities import AuthResult
from auth_strategy.domain.interfaces import AuthenticationStrategy


class StubStrategy(AuthenticationStrategy):
    def __init__(self, success: bool) -> None:
        self._success = success

    def authenticate(self, credentials: dict[str, object]) -> AuthResult:
        return AuthResult(success=self._success, strategy_name=self.get_name())

    def get_name(self) -> str:
        return "stub"


def test_authenticate_raises_without_strategy() -> None:
    authenticator = Authenticator()

    with pytest.raises(NoStrategyConfiguredError):
        authenticator.authenticate({})


def test_authenticate_delegates_to_configured_strategy() -> None:
    authenticator = Authenticator(StubStrategy(success=True))

    result = authenticator.authenticate({})

    assert result.success is True


def test_set_strategy_swaps_strategy_at_runtime() -> None:
    authenticator = Authenticator(StubStrategy(success=True))

    authenticator.set_strategy(StubStrategy(success=False))
    result = authenticator.authenticate({})

    assert result.success is False
    assert authenticator.current_strategy is not None
