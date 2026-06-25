"""Domain entities for the Compression Strategy CLI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionResult:
    """Immutable outcome of compressing (or decompressing) a payload."""

    original_size: int
    output_size: int
    strategy_name: str

    @property
    def ratio(self) -> float:
        """Output size as a fraction of the original (0..1, lower is smaller)."""
        if self.original_size == 0:
            return 0.0
        return self.output_size / self.original_size
