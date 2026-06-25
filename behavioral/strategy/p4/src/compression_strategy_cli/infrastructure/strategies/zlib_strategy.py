"""ZlibCompressionStrategy — wraps the stdlib zlib codec."""

from __future__ import annotations

import zlib

from compression_strategy_cli.domain.interfaces import CompressionStrategy


class ZlibCompressionStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)

    def get_name(self) -> str:
        return "zlib"

    def get_file_extension(self) -> str:
        return ".zlib"
