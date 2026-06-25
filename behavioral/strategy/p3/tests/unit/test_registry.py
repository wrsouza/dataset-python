"""Unit tests for the strategy registry."""

from __future__ import annotations

import pytest

from auth_strategy.domain.exceptions import InvalidStrategyError
from auth_strategy.infrastructure.strategies.password import PasswordAuthStrategy
from auth_strategy.infrastructure.strategies.registry import (
    get_strategy,
    list_strategy_names,
)


def test_get_strategy_resolves_password_strategy() -> None:
    strategy = get_strategy("password")

    assert isinstance(strategy, PasswordAuthStrategy)


def test_get_strategy_is_case_insensitive() -> None:
    strategy = get_strategy("TOKEN")

    assert strategy.get_name() == "token"


def test_get_strategy_raises_for_unknown_name() -> None:
    with pytest.raises(InvalidStrategyError):
        get_strategy("unknown")


def test_list_strategy_names_includes_all_registered() -> None:
    names = list_strategy_names()

    assert names == ["oauth", "password", "token"]
