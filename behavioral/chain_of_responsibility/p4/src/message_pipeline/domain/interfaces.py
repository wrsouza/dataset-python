"""Abstractions for the Chain of Responsibility message handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from message_pipeline.domain.entities import IncomingMessage, ProcessingStep


class MessageHandler(ABC):
    """A single link in the message processing chain.

    Each handler inspects the message and decides whether it can reach
    a final verdict. If not, it forwards the message to the next handler
    in the chain, if any.
    """

    _next_handler: MessageHandler | None = None

    def set_next(self, handler: MessageHandler) -> MessageHandler:
        """Wire the next handler in the chain and return it for fluent chaining."""
        self._next_handler = handler
        return handler

    def handle(self, message: IncomingMessage) -> IncomingMessage:
        """Attempt to reach a verdict, otherwise pass it along the chain."""
        verdict = self._inspect(message)
        if verdict is not None:
            message.record_step(verdict)
            return message
        if self._next_handler is not None:
            return self._next_handler.handle(message)
        return message

    @abstractmethod
    def _inspect(self, message: IncomingMessage) -> ProcessingStep | None:
        """Return a ProcessingStep verdict, or None to defer to the next handler."""


class QueueConsumer(ABC):
    """Boundary for consuming messages from a message broker queue."""

    @abstractmethod
    def consume(self, queue: str, limit: int) -> Iterator[IncomingMessage]:
        """Yield up to `limit` messages from the given queue."""

    @abstractmethod
    def ack(self, message: IncomingMessage) -> None:
        """Acknowledge that a message was processed."""
