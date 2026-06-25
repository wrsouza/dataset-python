"""Unit tests for KafkaStreamIterator, the concrete GoF Iterator."""

from __future__ import annotations

import pytest

from stream_iterator.domain.entities import StreamMessage
from stream_iterator.domain.interfaces import MessageSource
from stream_iterator.infrastructure.stream_iterator import KafkaStreamIterator


class FakeMessageSource(MessageSource):
    """An in-memory MessageSource that returns one batch per poll call."""

    def __init__(self, batches: list[list[StreamMessage]]) -> None:
        self._batches = batches
        self.poll_calls = 0

    def poll(self, timeout_ms: int) -> list[StreamMessage]:
        self.poll_calls += 1
        if not self._batches:
            return []
        return self._batches.pop(0)


def _msg(offset: int) -> StreamMessage:
    return StreamMessage(key=None, value={}, offset=offset, partition=0)


def test_iterates_all_messages_from_a_single_batch() -> None:
    source = FakeMessageSource([[_msg(0), _msg(1), _msg(2)]])
    iterator = KafkaStreamIterator(source)

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().offset)

    assert seen == [0, 1, 2]


def test_stops_after_first_empty_poll() -> None:
    source = FakeMessageSource([[_msg(0)], []])
    iterator = KafkaStreamIterator(source)

    iterator.next()

    assert iterator.has_next() is False
    assert source.poll_calls == 2


def test_continues_polling_across_non_empty_batches() -> None:
    source = FakeMessageSource([[_msg(0)], [_msg(1)]])
    iterator = KafkaStreamIterator(source)

    seen = []
    while iterator.has_next():
        seen.append(iterator.next().offset)

    assert seen == [0, 1]


def test_has_next_is_false_when_nothing_available() -> None:
    source = FakeMessageSource([[]])
    iterator = KafkaStreamIterator(source)

    assert iterator.has_next() is False


def test_next_raises_stop_iteration_when_exhausted() -> None:
    source = FakeMessageSource([[_msg(0)]])
    iterator = KafkaStreamIterator(source)
    iterator.next()

    with pytest.raises(StopIteration):
        iterator.next()
