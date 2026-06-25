"""FileCompressor context — uses CompressionStrategy via composition,
swappable at runtime."""

from __future__ import annotations

from compression_strategy_cli.domain.entities import CompressionResult
from compression_strategy_cli.domain.interfaces import CompressionStrategy


class NoStrategyConfiguredError(Exception):
    def __init__(self) -> None:
        super().__init__("No compression strategy configured")


class FileCompressor:
    """Context that delegates compression to a pluggable CompressionStrategy.

    DIP: depends on CompressionStrategy ABC, not concrete implementations.
    """

    def __init__(self, strategy: CompressionStrategy | None = None) -> None:
        self._strategy: CompressionStrategy | None = strategy

    def set_strategy(self, strategy: CompressionStrategy) -> None:
        self._strategy = strategy

    @property
    def current_strategy(self) -> CompressionStrategy | None:
        return self._strategy

    def compress(self, data: bytes) -> tuple[bytes, CompressionResult]:
        strategy = self._require_strategy()
        compressed = strategy.compress(data)
        result = CompressionResult(
            original_size=len(data),
            output_size=len(compressed),
            strategy_name=strategy.get_name(),
        )
        return compressed, result

    def decompress(self, data: bytes) -> tuple[bytes, CompressionResult]:
        strategy = self._require_strategy()
        decompressed = strategy.decompress(data)
        result = CompressionResult(
            original_size=len(data),
            output_size=len(decompressed),
            strategy_name=strategy.get_name(),
        )
        return decompressed, result

    def _require_strategy(self) -> CompressionStrategy:
        if self._strategy is None:
            raise NoStrategyConfiguredError()
        return self._strategy
