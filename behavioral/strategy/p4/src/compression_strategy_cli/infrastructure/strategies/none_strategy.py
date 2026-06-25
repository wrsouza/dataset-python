"""NoneCompressionStrategy — the null object: passes bytes through unchanged."""

from __future__ import annotations

from compression_strategy_cli.domain.interfaces import CompressionStrategy


class NoneCompressionStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data

    def get_name(self) -> str:
        return "none"

    def get_file_extension(self) -> str:
        return ".raw"
