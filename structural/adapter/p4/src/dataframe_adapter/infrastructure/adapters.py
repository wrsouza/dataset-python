"""Concrete Adapters — translate each Adaptee (parser library) to the Target.

Design decision: we use **pandas as the single Adaptee for all three
formats** (CSV, JSON, Parquet) instead of mixing the stdlib `csv`/`json`
modules with pandas only for Parquet. Rationale:

* Consistency: a single library handles type inference, encoding and quoting
  edge cases identically across formats, so adapters differ only in *which
  pandas reader* they call — making the Adapter pattern's translation step
  obvious and symmetrical.
* Parquet has no stdlib reader; pandas (backed by pyarrow) is required
  there anyway. Reusing it for CSV/JSON avoids a second set of parsing
  semantics (e.g. quoting rules, NaN handling) that a student would have to
  reconcile mentally between stdlib and pandas.
* Each adapter still has a single, narrow responsibility (SRP): translate
  *one* pandas reader's DataFrame into the domain's ParsedDataset.

Every adapter converts cell values to ``str`` because ``ParsedDataset`` is a
text-oriented, format-agnostic representation — type fidelity (int vs float
vs str) is intentionally not preserved, matching the unified CSV export use
case (NormalizeToCsvUseCase).
"""

from __future__ import annotations

import io

import pandas as pd

from dataframe_adapter.domain.entities import InvalidDataError, ParsedDataset


def _dataframe_to_parsed_dataset(
    dataframe: pd.DataFrame, source_format: str
) -> ParsedDataset:
    """Translate a pandas DataFrame (Adaptee output) into a ParsedDataset."""
    columns = [str(column) for column in dataframe.columns]
    rows = [
        ["" if pd.isna(value) else str(value) for value in row]
        for row in dataframe.itertuples(index=False, name=None)
    ]
    return ParsedDataset(columns=columns, rows=rows, source_format=source_format)


class CsvAdapter:
    """Adapter: translates CSV bytes (via pandas' CSV reader) to the Target."""

    FORMAT_NAME = "csv"

    def load(self, raw_bytes: bytes) -> ParsedDataset:
        """Parse CSV *raw_bytes* into a ParsedDataset."""
        try:
            dataframe = pd.read_csv(io.BytesIO(raw_bytes))
        except (
            pd.errors.ParserError,
            pd.errors.EmptyDataError,
            UnicodeDecodeError,
        ) as exc:
            raise InvalidDataError(self.FORMAT_NAME, str(exc)) from exc
        return _dataframe_to_parsed_dataset(dataframe, self.FORMAT_NAME)


class JsonAdapter:
    """Adapter: translates JSON bytes (via pandas' JSON reader) to the Target."""

    FORMAT_NAME = "json"

    def load(self, raw_bytes: bytes) -> ParsedDataset:
        """Parse JSON *raw_bytes* into a ParsedDataset."""
        try:
            dataframe = pd.read_json(io.BytesIO(raw_bytes))
        except (ValueError, UnicodeDecodeError) as exc:
            raise InvalidDataError(self.FORMAT_NAME, str(exc)) from exc
        return _dataframe_to_parsed_dataset(dataframe, self.FORMAT_NAME)


class ParquetAdapter:
    """Adapter: translates Parquet bytes (via pandas/pyarrow) to the Target."""

    FORMAT_NAME = "parquet"

    def load(self, raw_bytes: bytes) -> ParsedDataset:
        """Parse Parquet *raw_bytes* into a ParsedDataset."""
        try:
            dataframe = pd.read_parquet(io.BytesIO(raw_bytes))
        except Exception as exc:  # pyarrow raises various low-level errors
            raise InvalidDataError(self.FORMAT_NAME, str(exc)) from exc
        return _dataframe_to_parsed_dataset(dataframe, self.FORMAT_NAME)
