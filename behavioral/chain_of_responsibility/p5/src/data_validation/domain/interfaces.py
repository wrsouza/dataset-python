"""Abstractions for the Chain of Responsibility validation handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from data_validation.domain.entities import DataRecord, ValidationStep


class ValidationHandler(ABC):
    """A single link in the data validation chain.

    Each handler inspects the record and decides whether it can reach a
    final verdict. If not, it forwards the record to the next handler in
    the chain, if any.
    """

    _next_handler: ValidationHandler | None = None

    def set_next(self, handler: ValidationHandler) -> ValidationHandler:
        """Wire the next handler in the chain and return it for fluent chaining."""
        self._next_handler = handler
        return handler

    def handle(self, record: DataRecord) -> DataRecord:
        """Attempt to reach a verdict, otherwise pass it along the chain."""
        verdict = self._inspect(record)
        if verdict is not None:
            record.record_step(verdict)
            return record
        if self._next_handler is not None:
            return self._next_handler.handle(record)
        return record

    @abstractmethod
    def _inspect(self, record: DataRecord) -> ValidationStep | None:
        """Return a ValidationStep verdict, or None to defer to the next handler."""
