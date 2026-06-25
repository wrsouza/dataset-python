"""Strategy registry — maps string keys to CompressionStrategy instances."""

from __future__ import annotations

from compression_strategy_cli.domain.exceptions import InvalidStrategyError
from compression_strategy_cli.domain.interfaces import CompressionStrategy
from compression_strategy_cli.infrastructure.strategies.bz2_strategy import (
    Bz2CompressionStrategy,
)
from compression_strategy_cli.infrastructure.strategies.gzip_strategy import (
    GzipCompressionStrategy,
)
from compression_strategy_cli.infrastructure.strategies.none_strategy import (
    NoneCompressionStrategy,
)
from compression_strategy_cli.infrastructure.strategies.zlib_strategy import (
    ZlibCompressionStrategy,
)

_STRATEGY_MAP: dict[str, CompressionStrategy] = {
    "gzip": GzipCompressionStrategy(),
    "zlib": ZlibCompressionStrategy(),
    "bz2": Bz2CompressionStrategy(),
    "none": NoneCompressionStrategy(),
}


def get_strategy(name: str) -> CompressionStrategy:
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
