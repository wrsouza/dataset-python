"""Use cases orchestrating message consumption and processing through the chain."""

from __future__ import annotations

from dataclasses import dataclass

from message_pipeline.domain.entities import IncomingMessage
from message_pipeline.domain.interfaces import MessageHandler, QueueConsumer


@dataclass
class ProcessBatchResult:
    """Outcome returned to callers after processing a batch of messages."""

    messages: list[IncomingMessage]


class ProcessMessageUseCase:
    """Routes a single message through the processing chain."""

    def __init__(self, chain: MessageHandler) -> None:
        self._chain = chain

    def execute(self, message: IncomingMessage) -> IncomingMessage:
        return self._chain.handle(message)


class ConsumeAndProcessUseCase:
    """Consumes up to `limit` messages from a queue and processes each."""

    def __init__(self, consumer: QueueConsumer, chain: MessageHandler) -> None:
        self._consumer = consumer
        self._chain = chain

    def execute(self, queue: str, limit: int) -> ProcessBatchResult:
        processed: list[IncomingMessage] = []
        for message in self._consumer.consume(queue, limit):
            result = self._chain.handle(message)
            self._consumer.ack(result)
            processed.append(result)
        return ProcessBatchResult(messages=processed)
