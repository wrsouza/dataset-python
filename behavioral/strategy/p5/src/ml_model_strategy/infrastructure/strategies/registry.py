"""Strategy registry — maps string keys to MLModelStrategy instances."""

from __future__ import annotations

from ml_model_strategy.domain.exceptions import InvalidStrategyError
from ml_model_strategy.domain.interfaces import MLModelStrategy
from ml_model_strategy.infrastructure.strategies.decision_tree import (
    DecisionTreeStrategy,
)
from ml_model_strategy.infrastructure.strategies.linear_regression import (
    LinearRegressionStrategy,
)
from ml_model_strategy.infrastructure.strategies.random_forest import (
    RandomForestStrategy,
)

_STRATEGY_MAP: dict[str, MLModelStrategy] = {
    "linear_regression": LinearRegressionStrategy(),
    "decision_tree": DecisionTreeStrategy(),
    "random_forest": RandomForestStrategy(),
}


def get_strategy(name: str) -> MLModelStrategy:
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
