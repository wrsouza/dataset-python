"""Abstractions for the Iterator pattern and the underlying Kafka access."""

from __future__ import annotations

from abc import ABC, abstractmethod

from stream_iterator.domain.entities import StreamMessage


class MessageIterator(ABC):
    """The Iterator: traverses the messages currently available on a topic,

    one at a time, without exposing how (or how many per poll) Kafka was
    actually polled underneath.
    """

    @abstractmethod
    def has_next(self) -> bool:
        """Return True if there is at least one more message to traverse."""

    @abstractmethod
    def next(self) -> StreamMessage:
        """Return the next message and advance the iterator's position."""


class MessageSource(ABC):
    """The Aggregate's data-access boundary: polls a Kafka topic for new records."""

    @abstractmethod
    def poll(self, timeout_ms: int) -> list[StreamMessage]:
        """Return whatever messages are immediately available, or an empty list."""
