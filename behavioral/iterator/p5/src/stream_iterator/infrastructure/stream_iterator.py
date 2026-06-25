"""Concrete Iterator: drains the messages currently available on a topic."""

from __future__ import annotations

from collections import deque

from stream_iterator.domain.entities import StreamMessage
from stream_iterator.domain.interfaces import MessageIterator, MessageSource


class KafkaStreamIterator(MessageIterator):
    """Traverses the messages currently available on a topic, one at a time.

    A single empty poll means "nothing more right now" and ends the
    traversal — this models draining a snapshot of the stream (e.g. for
    one Streamlit button click), not blocking forever like a live
    `for message in consumer` loop would.
    """

    def __init__(self, source: MessageSource, poll_timeout_ms: int = 1000) -> None:
        self._source = source
        self._poll_timeout_ms = poll_timeout_ms
        self._buffer: deque[StreamMessage] = deque()
        self._exhausted = False

    def has_next(self) -> bool:
        if not self._buffer and not self._exhausted:
            self._poll_once()
        return bool(self._buffer)

    def next(self) -> StreamMessage:
        if not self.has_next():
            raise StopIteration("No more messages currently available")
        return self._buffer.popleft()

    def _poll_once(self) -> None:
        messages = self._source.poll(self._poll_timeout_ms)
        if not messages:
            self._exhausted = True
            return
        self._buffer.extend(messages)
