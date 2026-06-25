"""GzipCompressionStrategy — wraps the stdlib gzip codec."""

from __future__ import annotations

import gzip

from compression_strategy_cli.domain.interfaces import CompressionStrategy


class GzipCompressionStrategy(CompressionStrategy):
    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)

    def get_name(self) -> str:
        return "gzip"

    def get_file_extension(self) -> str:
        return ".gz"
