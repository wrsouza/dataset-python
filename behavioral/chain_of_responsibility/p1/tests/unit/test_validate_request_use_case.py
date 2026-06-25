"""Unit tests for the use case that assembles and runs the chain."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from validation.application.validate_request_use_case import (
    ValidateRequestUseCase,
    build_default_chain,
)
from validation.domain.entities import APIRequest, APIResponse


def test_build_default_chain_links_handlers_in_order() -> None:
    first = MagicMock()
    second = MagicMock()
    third = MagicMock()

    entry_point = build_default_chain(first, second, third)

    assert entry_point is first
    first.set_next.assert_called_once_with(second)
    second.set_next.assert_called_once_with(third)
    third.set_next.assert_not_called()


def test_build_default_chain_raises_without_handlers() -> None:
    with pytest.raises(ValueError, match="At least one handler"):
        build_default_chain()


def test_build_default_chain_with_single_handler_does_not_link() -> None:
    only_handler = MagicMock()

    entry_point = build_default_chain(only_handler)

    assert entry_point is only_handler
    only_handler.set_next.assert_not_called()


def test_execute_returns_handler_short_circuit_response() -> None:
    short_circuit = APIResponse.unauthorized("nope", handler_name="X")
    entry_handler = MagicMock(handle=MagicMock(return_value=short_circuit))
    use_case = ValidateRequestUseCase(entry_handler=entry_handler)

    result = use_case.execute(APIRequest(body={}))

    assert result is short_circuit


def test_execute_returns_default_success_when_chain_completes() -> None:
    entry_handler = MagicMock(handle=MagicMock(return_value=None))
    use_case = ValidateRequestUseCase(entry_handler=entry_handler)

    result = use_case.execute(APIRequest(body={}))

    assert result.is_success
    assert result.status_code == 200
