"""Unit tests for the CompressionResult domain entity."""

from __future__ import annotations

from compression_strategy_cli.domain.entities import CompressionResult


def test_ratio_computes_output_over_original() -> None:
    result = CompressionResult(original_size=100, output_size=25, strategy_name="gzip")

    assert result.ratio == 0.25


def test_ratio_is_zero_when_original_size_is_zero() -> None:
    result = CompressionResult(original_size=0, output_size=0, strategy_name="gzip")

    assert result.ratio == 0.0
