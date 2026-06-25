"""Abstractions for the structured logger domain.

Defines the contract that any logger implementation must satisfy, and the
contract for handlers that consume emitted log records.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from src.logger.domain.entities import LogRecord


class AbstractLogger(ABC):
    """Contract for a structured logger.

    Any concrete logger (singleton or not) must implement these methods.
    Kept intentionally small (ISP) — only logging operations, no handler
    management leaks into this interface.
    """

    @abstractmethod
    def log(self, level: int, message: str, **context: Any) -> LogRecord:
        """Emit a log record at the given severity level."""

    @abstractmethod
    def set_context(self, **context: Any) -> None:
        """Attach persistent key-value context to all future records."""


class LogHandlerProtocol(Protocol):
    """Structural contract for anything that can consume a LogRecord.

    Using Protocol (vs. ABC) keeps handlers decoupled from the logger
    module — any object with an `emit` method qualifies (duck typing).
    """

    def emit(self, record: LogRecord) -> None:
        """Write the record to its destination (stdout, file, etc.)."""
        ...
