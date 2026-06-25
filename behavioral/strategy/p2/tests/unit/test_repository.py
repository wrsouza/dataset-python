"""Unit tests for DiscountHistoryRepository against a real (in-memory SQLite)
DB-API connection."""

from __future__ import annotations

from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.infrastructure.repository import DiscountHistoryRepository


def test_append_and_list_all_round_trips_result(
    repository: DiscountHistoryRepository,
) -> None:
    result = DiscountResult(
        original_total=100.0,
        discount_amount=10.0,
        final_total=90.0,
        strategy_name="percentage",
    )
    repository.append(result)

    history = repository.list_all()

    assert history == [result]


def test_list_all_returns_results_in_insertion_order(
    repository: DiscountHistoryRepository,
) -> None:
    first = DiscountResult(
        original_total=100.0, discount_amount=10.0, final_total=90.0, strategy_name="a"
    )
    second = DiscountResult(
        original_total=200.0, discount_amount=20.0, final_total=180.0, strategy_name="b"
    )
    repository.append(first)
    repository.append(second)

    history = repository.list_all()

    assert [r.strategy_name for r in history] == ["a", "b"]


def test_list_all_empty_when_no_history(repository: DiscountHistoryRepository) -> None:
    assert repository.list_all() == []
