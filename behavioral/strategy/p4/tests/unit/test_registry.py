"""Unit tests for the strategy registry."""

from __future__ import annotations

import pytest

from compression_strategy_cli.domain.exceptions import InvalidStrategyError
from compression_strategy_cli.infrastructure.strategies.gzip_strategy import (
    GzipCompressionStrategy,
)
from compression_strategy_cli.infrastructure.strategies.registry import (
    get_strategy,
    list_strategy_names,
)


def test_get_strategy_resolves_gzip() -> None:
    strategy = get_strategy("gzip")

    assert isinstance(strategy, GzipCompressionStrategy)


def test_get_strategy_is_case_insensitive() -> None:
    strategy = get_strategy("GZIP")

    assert strategy.get_name() == "gzip"


def test_get_strategy_raises_for_unknown_name() -> None:
    with pytest.raises(InvalidStrategyError):
        get_strategy("unknown")


def test_list_strategy_names_includes_all_registered() -> None:
    assert list_strategy_names() == ["bz2", "gzip", "none", "zlib"]
