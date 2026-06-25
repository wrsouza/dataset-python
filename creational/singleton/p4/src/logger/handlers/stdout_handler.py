"""Concrete log handler that writes JSON-formatted records to stdout."""

from __future__ import annotations

import json
import sys

from src.logger.domain.entities import LogRecord


class StdoutJsonHandler:
    """Writes each LogRecord as a single JSON line to stdout.

    Satisfies LogHandlerProtocol structurally — no inheritance needed.
    """

    def emit(self, record: LogRecord) -> None:
        """Serialise the record to JSON and print it to stdout."""
        line = json.dumps(record.to_dict(), ensure_ascii=False)
        sys.stdout.write(line + "\n")
