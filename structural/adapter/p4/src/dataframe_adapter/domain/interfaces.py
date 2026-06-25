"""Target interface — TabularDataSource Protocol.

Defines the unified interface that every format-specific Adapter must
implement. Client code (use cases, Streamlit UI) depends ONLY on this
abstraction (DIP), never on csv/json/pandas/pyarrow directly.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from dataframe_adapter.domain.entities import ParsedDataset


@runtime_checkable
class TabularDataSource(Protocol):
    """Target: unified interface to load tabular data from raw bytes.

    ISP — a single, narrow method; no format-specific detail leaks out.
    DIP — application and UI depend on this Protocol, never on a concrete
    parser (csv module, json module, pandas, pyarrow).
    LSP — every adapter must honour the same contract: valid bytes produce
    a ParsedDataset, invalid bytes raise InvalidDataError.
    """

    def load(self, raw_bytes: bytes) -> ParsedDataset:
        """Parse *raw_bytes* and return a format-agnostic ParsedDataset."""
        ...
