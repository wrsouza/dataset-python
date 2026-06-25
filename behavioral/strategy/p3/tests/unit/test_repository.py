"""Unit tests for DjangoAuthAttemptLogRepository."""

from __future__ import annotations

import pytest

from auth_strategy.domain.entities import AuthResult
from auth_strategy.infrastructure.repository import DjangoAuthAttemptLogRepository

pytestmark = pytest.mark.django_db


def test_append_and_list_all_round_trips_result() -> None:
    repository = DjangoAuthAttemptLogRepository()
    result = AuthResult(success=True, strategy_name="password", user_id="u1")

    repository.append(result)

    history = repository.list_all()
    assert history == [result]


def test_list_all_returns_results_in_insertion_order() -> None:
    repository = DjangoAuthAttemptLogRepository()
    repository.append(AuthResult(success=True, strategy_name="password", user_id="u1"))
    repository.append(AuthResult(success=False, strategy_name="token", reason="bad"))

    history = repository.list_all()

    assert [r.strategy_name for r in history] == ["password", "token"]


def test_list_all_empty_when_no_attempts() -> None:
    repository = DjangoAuthAttemptLogRepository()

    assert repository.list_all() == []
