"""Unit tests for the FileCompressor context."""

from __future__ import annotations

import pytest

from compression_strategy_cli.application.context import (
    FileCompressor,
    NoStrategyConfiguredError,
)
from compression_strategy_cli.infrastructure.strategies.gzip_strategy import (
    GzipCompressionStrategy,
)
from compression_strategy_cli.infrastructure.strategies.none_strategy import (
    NoneCompressionStrategy,
)


def test_compress_raises_without_strategy() -> None:
    compressor = FileCompressor()

    with pytest.raises(NoStrategyConfiguredError):
        compressor.compress(b"data")


def test_decompress_raises_without_strategy() -> None:
    compressor = FileCompressor()

    with pytest.raises(NoStrategyConfiguredError):
        compressor.decompress(b"data")


def test_compress_delegates_to_configured_strategy() -> None:
    compressor = FileCompressor(GzipCompressionStrategy())

    compressed, result = compressor.compress(b"hello world" * 10)

    assert result.strategy_name == "gzip"
    assert result.original_size == len(b"hello world" * 10)
    assert result.output_size == len(compressed)


def test_set_strategy_swaps_strategy_at_runtime() -> None:
    compressor = FileCompressor(GzipCompressionStrategy())

    compressor.set_strategy(NoneCompressionStrategy())
    _, result = compressor.compress(b"data")

    assert result.strategy_name == "none"
    assert compressor.current_strategy is not None
    assert compressor.current_strategy.get_name() == "none"
