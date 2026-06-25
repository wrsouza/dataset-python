"""Use cases orchestrating the StructuredLogger singleton.

These functions are the composition boundary used by the CLI: they depend
only on AbstractLogger (DIP) and never instantiate concrete loggers
themselves — the singleton instance is obtained via get_logger().
"""

from __future__ import annotations

from typing import Any

from src.logger.domain.entities import LogLevel, LogRecord
from src.logger.domain.interfaces import AbstractLogger
from src.logger.handlers.stdout_handler import StdoutJsonHandler
from src.logger.infrastructure.singleton import StructuredLogger


def get_logger(min_level: LogLevel = LogLevel.INFO) -> StructuredLogger:
    """Return the process-wide StructuredLogger, wiring a stdout handler.

    Safe to call repeatedly: thanks to SingletonMeta, the constructor
    arguments only take effect on first creation; subsequent calls return
    the existing instance untouched.
    """
    logger = StructuredLogger(min_level=min_level)
    if not logger.stats.handler_count:
        logger.add_handler(StdoutJsonHandler())
    return logger


class EmitLogMessageUseCase:
    """Emits a single structured log message through the shared logger.

    Depends on AbstractLogger (abstraction), not on StructuredLogger
    directly — satisfies Dependency Inversion and keeps this use case
    testable with a fake logger.
    """

    def __init__(self, logger: AbstractLogger) -> None:
        self._logger = logger

    def execute(self, level: LogLevel, message: str, **context: Any) -> LogRecord:
        """Log `message` at `level` with the given extra context."""
        return self._logger.log(int(level), message, **context)


class SetLoggerContextUseCase:
    """Sets persistent global context on the shared logger."""

    def __init__(self, logger: AbstractLogger) -> None:
        self._logger = logger

    def execute(self, **context: Any) -> None:
        """Attach key-value pairs to every subsequent log record."""
        self._logger.set_context(**context)
