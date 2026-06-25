"""Unit tests for the concrete compression strategies — every strategy must
round-trip compress/decompress for arbitrary bytes."""

from __future__ import annotations

import pytest

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

ALL_STRATEGIES = [
    GzipCompressionStrategy(),
    ZlibCompressionStrategy(),
    Bz2CompressionStrategy(),
    NoneCompressionStrategy(),
]


@pytest.mark.parametrize("strategy", ALL_STRATEGIES)
def test_compress_then_decompress_round_trips(strategy: object) -> None:
    data = b"the quick brown fox jumps over the lazy dog" * 20

    compressed = strategy.compress(data)  # type: ignore[attr-defined]
    decompressed = strategy.decompress(compressed)  # type: ignore[attr-defined]

    assert decompressed == data


@pytest.mark.parametrize("strategy", ALL_STRATEGIES)
def test_get_name_and_extension_are_non_empty(strategy: object) -> None:
    assert strategy.get_name()  # type: ignore[attr-defined]
    assert strategy.get_file_extension().startswith(".")  # type: ignore[attr-defined]


def test_gzip_actually_shrinks_repetitive_data() -> None:
    data = b"a" * 10_000

    compressed = GzipCompressionStrategy().compress(data)

    assert len(compressed) < len(data)


def test_none_strategy_does_not_change_size() -> None:
    data = b"unchanged"

    compressed = NoneCompressionStrategy().compress(data)

    assert compressed == data
