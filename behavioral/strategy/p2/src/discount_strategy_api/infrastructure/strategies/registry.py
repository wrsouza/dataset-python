"""Strategy registry — builds a DiscountStrategy from a name and params."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from discount_strategy_api.domain.exceptions import InvalidStrategyError
from discount_strategy_api.domain.interfaces import DiscountStrategy
from discount_strategy_api.infrastructure.strategies.bulk_quantity import (
    BulkQuantityDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.fixed_amount import (
    FixedAmountDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.no_discount import (
    NoDiscountStrategy,
)
from discount_strategy_api.infrastructure.strategies.percentage import (
    PercentageDiscountStrategy,
)

_STRATEGY_FACTORIES: dict[str, Callable[[dict[str, Any]], DiscountStrategy]] = {
    "percentage": lambda params: PercentageDiscountStrategy(
        percentage=params["percentage"]
    ),
    "fixed_amount": lambda params: FixedAmountDiscountStrategy(amount=params["amount"]),
    "bulk_quantity": lambda params: BulkQuantityDiscountStrategy(
        threshold=params["threshold"], percentage=params["percentage"]
    ),
    "no_discount": lambda params: NoDiscountStrategy(),
}


def get_strategy(name: str, params: dict[str, Any] | None = None) -> DiscountStrategy:
    """Build a strategy instance by name.

    Raises:
        InvalidStrategyError: when name is not registered.
    """
    factory = _STRATEGY_FACTORIES.get(name.lower())
    if factory is None:
        raise InvalidStrategyError(name)
    return factory(params or {})


def list_strategy_names() -> list[str]:
    return sorted(_STRATEGY_FACTORIES)
