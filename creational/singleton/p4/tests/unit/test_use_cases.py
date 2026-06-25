"""Unit tests for application use cases — exercised with a fake logger."""

from __future__ import annotations

from typing import Any

from src.logger.application.use_cases import (
    EmitLogMessageUseCase,
    SetLoggerContextUseCase,
    get_logger,
)
from src.logger.domain.entities import LogLevel, LogRecord
from src.logger.domain.interfaces import AbstractLogger


class _FakeLogger(AbstractLogger):
    def __init__(self) -> None:
        self.logged: list[tuple[int, str, dict[str, Any]]] = []
        self.context: dict[str, Any] = {}

    def log(self, level: int, message: str, **context: Any) -> LogRecord:
        self.logged.append((level, message, context))
        return LogRecord(
            timestamp="2026-01-01T00:00:00+00:00",
            level=LogLevel(level),
            message=message,
            module="test",
            context=context,
            logger_ctx=self.context,
        )

    def set_context(self, **context: Any) -> None:
        self.context.update(context)


def test_emit_log_message_use_case_delegates_to_logger() -> None:
    fake = _FakeLogger()
    use_case = EmitLogMessageUseCase(logger=fake)

    record = use_case.execute(LogLevel.WARNING, "disk almost full", host="srv-1")

    assert fake.logged == [(LogLevel.WARNING, "disk almost full", {"host": "srv-1"})]
    assert record.message == "disk almost full"


def test_set_logger_context_use_case_delegates_to_logger() -> None:
    fake = _FakeLogger()
    use_case = SetLoggerContextUseCase(logger=fake)

    use_case.execute(service="payments")

    assert fake.context == {"service": "payments"}


def test_get_logger_wires_a_handler_exactly_once() -> None:
    logger = get_logger()
    same_logger = get_logger()

    assert logger is same_logger
    assert logger.stats.handler_count == 1
