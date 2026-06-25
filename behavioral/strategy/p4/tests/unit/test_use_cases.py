"""Unit tests for the Compression Strategy CLI use cases, using real
temporary files."""

from __future__ import annotations

from pathlib import Path

import pytest

from compression_strategy_cli.application.use_cases import (
    CompressFileInput,
    CompressFileUseCase,
    DecompressFileInput,
    DecompressFileUseCase,
)
from compression_strategy_cli.domain.exceptions import InvalidStrategyError


def test_compress_file_writes_output_with_extension(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    input_path.write_bytes(b"hello world" * 50)

    output_path, result = CompressFileUseCase().execute(
        CompressFileInput(input_path=input_path, strategy_name="gzip")
    )

    assert output_path.name == "data.txt.gz"
    assert output_path.exists()
    assert result.original_size == len(b"hello world" * 50)


def test_decompress_file_restores_original_content(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    original = b"hello world" * 50
    input_path.write_bytes(original)
    compressed_path, _ = CompressFileUseCase().execute(
        CompressFileInput(input_path=input_path, strategy_name="gzip")
    )

    output_path, result = DecompressFileUseCase().execute(
        DecompressFileInput(input_path=compressed_path, strategy_name="gzip")
    )

    assert output_path.name == "data.txt"
    assert output_path.read_bytes() == original
    assert result.output_size == len(original)


def test_compress_file_raises_for_unknown_strategy(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    input_path.write_bytes(b"data")

    with pytest.raises(InvalidStrategyError):
        CompressFileUseCase().execute(
            CompressFileInput(input_path=input_path, strategy_name="unknown")
        )
