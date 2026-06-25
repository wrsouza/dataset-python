"""Bz2CompressionStrategy — wraps the stdlib bz2 codec."""

from __future__ import annotations

import bz2

from compression_strategy_cli.domain.interfaces import CompressionStrategy


class Bz2CompressionStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return bz2.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return bz2.decompress(data)

    def get_name(self) -> str:
        return "bz2"

    def get_file_extension(self) -> str:
        return ".bz2"
