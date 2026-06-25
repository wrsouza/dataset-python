"""Thread-safe Singleton metaclass and the StructuredLogger implementation.

The Singleton pattern is realised via a metaclass: any class using
`SingletonMeta` as its metaclass will only ever be instantiated once per
process, regardless of how many times its constructor is called. A lock
guards the check-and-create step so concurrent threads cannot create two
separate instances (classic double-checked locking).
"""

from __future__ import annotations

import threading
from abc import ABCMeta
from datetime import UTC, datetime
from typing import Any, ClassVar

from src.logger.domain.entities import LoggerStats, LogLevel, LogRecord
from src.logger.domain.interfaces import AbstractLogger, LogHandlerProtocol


class SingletonMeta(ABCMeta):
    """Metaclass enforcing a single instance per class, thread-safe.

    Each class that uses this metaclass gets its own entry in `_instances`,
    so the same metaclass can be reused by unrelated singleton classes
    without them sharing state.
    """

    _instances: ClassVar[dict[type, Any]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class StructuredLogger(AbstractLogger, metaclass=SingletonMeta):
    """Singleton structured logger producing JSON log records.

    Only one instance exists per process (enforced by SingletonMeta). All
    callers across the application share the same instance, the same
    registered handlers, and the same global context.
    """

    def __init__(self, min_level: LogLevel = LogLevel.INFO) -> None:
        self._min_level = min_level
        self._handlers: list[LogHandlerProtocol] = []
        self._global_context: dict[str, Any] = {}
        self._stats = LoggerStats()
        self._write_lock = threading.Lock()

    def add_handler(self, handler: LogHandlerProtocol) -> None:
        """Register a handler that will receive every emitted record."""
        self._handlers.append(handler)
        self._stats.handler_count = len(self._handlers)

    def set_context(self, **context: Any) -> None:
        """Merge the given key-value pairs into the global log context."""
        self._global_context.update(context)
        self._stats.active_context_keys = list(self._global_context.keys())

    def clear_context(self) -> None:
        """Remove all global context previously set via set_context()."""
        self._global_context.clear()
        self._stats.active_context_keys = []

    def log(self, level: int, message: str, **context: Any) -> LogRecord:
        """Build a LogRecord and dispatch it to all registered handlers."""
        record = self._build_record(LogLevel(level), message, context)
        if level >= self._min_level:
            self._dispatch(record)
        return record

    def debug(self, message: str, **context: Any) -> LogRecord:
        """Convenience wrapper for log(DEBUG, ...)."""
        return self.log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context: Any) -> LogRecord:
        """Convenience wrapper for log(INFO, ...)."""
        return self.log(LogLevel.INFO, message, **context)

    def warning(self, message: str, **context: Any) -> LogRecord:
        """Convenience wrapper for log(WARNING, ...)."""
        return self.log(LogLevel.WARNING, message, **context)

    def error(self, message: str, **context: Any) -> LogRecord:
        """Convenience wrapper for log(ERROR, ...)."""
        return self.log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context: Any) -> LogRecord:
        """Convenience wrapper for log(CRITICAL, ...)."""
        return self.log(LogLevel.CRITICAL, message, **context)

    @property
    def stats(self) -> LoggerStats:
        """Expose aggregate counters for observability/testing."""
        return self._stats

    def _build_record(
        self, level: LogLevel, message: str, context: dict[str, Any]
    ) -> LogRecord:
        return LogRecord(
            timestamp=datetime.now(tz=UTC).isoformat(),
            level=level,
            message=message,
            module=context.pop("module", __name__),
            context=context,
            logger_ctx=dict(self._global_context),
        )

    def _dispatch(self, record: LogRecord) -> None:
        with self._write_lock:
            self._stats.increment(record.level)
            for handler in self._handlers:
                handler.emit(record)


def reset_singleton_for_tests() -> None:
    """Clear the SingletonMeta registry entry for StructuredLogger.

    Test-only helper: production code never needs to "un-singleton" a
    class. Exposed here (infrastructure layer) so tests don't reach into
    metaclass internals directly.
    """
    SingletonMeta._instances.pop(StructuredLogger, None)
