"""Application use cases for the Discount Strategy API.

Each use case has a single responsibility and depends only on
abstractions (DIP): the DiscountCalculator context and the history
repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from discount_strategy_api.application.context import DiscountCalculator
from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.infrastructure.repository import DiscountHistoryRepository
from discount_strategy_api.infrastructure.strategies.registry import get_strategy


@dataclass
class ApplyDiscountInput:
    strategy_name: str
    original_total: float
    quantity: int
    params: dict[str, Any]


class ApplyDiscountUseCase:
    def __init__(self, repository: DiscountHistoryRepository) -> None:
        self._repository = repository

    def execute(self, data: ApplyDiscountInput) -> DiscountResult:
        strategy = get_strategy(data.strategy_name, data.params)
        calculator = DiscountCalculator(strategy)
        result = calculator.calculate(data.original_total, data.quantity)
        self._repository.append(result)
        return result


class GetDiscountHistoryUseCase:
    def __init__(self, repository: DiscountHistoryRepository) -> None:
        self._repository = repository

    def execute(self) -> list[DiscountResult]:
        return self._repository.list_all()
