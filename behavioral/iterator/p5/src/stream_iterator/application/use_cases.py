"""Use cases orchestrating message draining and stream summarisation."""

from __future__ import annotations

from collections.abc import Iterator as TypingIterator

from stream_iterator.domain.entities import StreamMessage, StreamSummary
from stream_iterator.domain.interfaces import MessageSource
from stream_iterator.infrastructure.stream_iterator import KafkaStreamIterator


class DrainAvailableMessagesUseCase:
    """Yields every message currently available on the topic, via the Iterator."""

    def __init__(self, source: MessageSource, poll_timeout_ms: int = 1000) -> None:
        self._source = source
        self._poll_timeout_ms = poll_timeout_ms

    def execute(self) -> TypingIterator[StreamMessage]:
        iterator = KafkaStreamIterator(self._source, self._poll_timeout_ms)
        while iterator.has_next():
            yield iterator.next()


class SummarizeAvailableMessagesUseCase:
    """Aggregates count and total `amount` across the currently available messages."""

    def __init__(self, source: MessageSource, poll_timeout_ms: int = 1000) -> None:
        self._source = source
        self._poll_timeout_ms = poll_timeout_ms

    def execute(self) -> tuple[StreamSummary, list[StreamMessage]]:
        iterator = KafkaStreamIterator(self._source, self._poll_timeout_ms)
        messages: list[StreamMessage] = []
        total_amount = 0.0

        while iterator.has_next():
            message = iterator.next()
            messages.append(message)
            amount = message.value.get("amount")
            if isinstance(amount, (int, float)):
                total_amount += float(amount)

        summary = StreamSummary(message_count=len(messages), total_amount=total_amount)
        return summary, messages
