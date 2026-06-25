"""Application layer — AdapterFactory and the normalization use case.

Depends only on the TabularDataSource abstraction (DIP); never imports a
concrete adapter directly except inside the factory, which is the single
composition point allowed to know about concrete classes.
"""

from __future__ import annotations

from pathlib import Path

from dataframe_adapter.domain.entities import ParsedDataset, UnsupportedFormatError
from dataframe_adapter.domain.interfaces import TabularDataSource
from dataframe_adapter.infrastructure.adapters import (
    CsvAdapter,
    JsonAdapter,
    ParquetAdapter,
)

_EXTENSION_TO_ADAPTER: dict[str, type[TabularDataSource]] = {
    ".csv": CsvAdapter,
    ".json": JsonAdapter,
    ".parquet": ParquetAdapter,
}


class AdapterFactory:
    """Detects the file format from its extension and returns the matching Adapter.

    OCP: supporting a new format means adding one entry to
    ``_EXTENSION_TO_ADAPTER`` and a new Adapter class — no existing adapter
    or client code is modified.
    """

    def create_for_filename(self, filename: str) -> TabularDataSource:
        """Return the TabularDataSource adapter matching *filename*'s extension."""
        extension = Path(filename).suffix.lower()
        adapter_class = _EXTENSION_TO_ADAPTER.get(extension)
        if adapter_class is None:
            raise UnsupportedFormatError(filename)
        return adapter_class()


class NormalizeToCsvUseCase:
    """Use case: receive uploaded bytes + filename, return a normalized CSV string.

    Delegates parsing entirely to the Adapter resolved by AdapterFactory and
    never inspects the original format beyond what TabularDataSource exposes
    (DIP) — adding a new format never requires touching this class (OCP).
    """

    def __init__(self, factory: AdapterFactory) -> None:
        self._factory = factory

    def execute(self, raw_bytes: bytes, filename: str) -> str:
        """Parse *raw_bytes* (named *filename*) and return normalized CSV text."""
        dataset = self.parse(raw_bytes, filename)
        return dataset.to_csv_text()

    def parse(self, raw_bytes: bytes, filename: str) -> ParsedDataset:
        """Parse *raw_bytes* and return the resulting ParsedDataset."""
        adapter = self._factory.create_for_filename(filename)
        return adapter.load(raw_bytes)
