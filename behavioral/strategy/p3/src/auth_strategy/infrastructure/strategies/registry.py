"""Strategy registry — maps string keys to AuthenticationStrategy instances."""

from __future__ import annotations

from auth_strategy.domain.exceptions import InvalidStrategyError
from auth_strategy.domain.interfaces import AuthenticationStrategy
from auth_strategy.infrastructure.strategies.oauth import OAuthStrategy
from auth_strategy.infrastructure.strategies.password import PasswordAuthStrategy
from auth_strategy.infrastructure.strategies.token import TokenAuthStrategy

_STRATEGY_MAP: dict[str, AuthenticationStrategy] = {
    "password": PasswordAuthStrategy(),
    "token": TokenAuthStrategy(),
    "oauth": OAuthStrategy(),
}


def get_strategy(name: str) -> AuthenticationStrategy:
    """Resolve a strategy by name.

    Raises:
        InvalidStrategyError: when name is not registered.
    """
    strategy = _STRATEGY_MAP.get(name.lower())
    if strategy is None:
        raise InvalidStrategyError(name)
    return strategy


def list_strategy_names() -> list[str]:
    return sorted(_STRATEGY_MAP)
