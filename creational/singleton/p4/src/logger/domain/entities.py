"""Domain entities for the structured logger.

Pure data classes — no I/O, no framework dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class LogLevel(IntEnum):
    """Log severity levels — ordered so that comparisons work naturally."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @property
    def label(self) -> str:
        return self.name


@dataclass(frozen=True)
class LogRecord:
    """Immutable log event passed from StructuredLogger to handlers.

    Fields:
        timestamp:  ISO-8601 UTC string set at capture time.
        level:      Severity level.
        message:    Human-readable description of the event.
        module:     __name__ of the calling module.
        context:    Arbitrary key-value pairs from the caller.
        logger_ctx: Global context injected by set_context().
    """

    timestamp: str
    level: LogLevel
    message: str
    module: str
    context: dict[str, Any]
    logger_ctx: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialise to the canonical JSON log format."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.label,
            "message": self.message,
            "module": self.module,
            "context": {**self.logger_ctx, **self.context},
        }


@dataclass
class LoggerStats:
    """Aggregate counters for the singleton logger instance."""

    records_emitted: int = 0
    records_by_level: dict[str, int] = field(default_factory=dict)
    handler_count: int = 0
    active_context_keys: list[str] = field(default_factory=list)

    def increment(self, level: LogLevel) -> None:
        self.records_emitted += 1
        self.records_by_level[level.label] = (
            self.records_by_level.get(level.label, 0) + 1
        )
