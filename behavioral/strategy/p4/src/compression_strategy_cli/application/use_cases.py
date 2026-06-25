"""Application use cases for the Compression Strategy CLI.

Each use case reads the input file, delegates to FileCompressor, and
writes the output file — the only place that touches the filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from compression_strategy_cli.application.context import FileCompressor
from compression_strategy_cli.domain.entities import CompressionResult
from compression_strategy_cli.infrastructure.strategies.registry import get_strategy


@dataclass
class CompressFileInput:
    input_path: Path
    strategy_name: str


class CompressFileUseCase:
    def execute(self, data: CompressFileInput) -> tuple[Path, CompressionResult]:
        strategy = get_strategy(data.strategy_name)
        compressor = FileCompressor(strategy)

        raw = data.input_path.read_bytes()
        compressed, result = compressor.compress(raw)

        output_path = data.input_path.with_suffix(
            data.input_path.suffix + strategy.get_file_extension()
        )
        output_path.write_bytes(compressed)
        return output_path, result


@dataclass
class DecompressFileInput:
    input_path: Path
    strategy_name: str


class DecompressFileUseCase:
    def execute(self, data: DecompressFileInput) -> tuple[Path, CompressionResult]:
        strategy = get_strategy(data.strategy_name)
        compressor = FileCompressor(strategy)

        raw = data.input_path.read_bytes()
        decompressed, result = compressor.decompress(raw)

        extension = strategy.get_file_extension()
        name = data.input_path.name
        stem = name[: -len(extension)] if name.endswith(extension) else name
        output_path = data.input_path.with_name(stem)
        output_path.write_bytes(decompressed)
        return output_path, result
