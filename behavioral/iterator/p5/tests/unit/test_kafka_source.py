"""Unit tests for KafkaMessageSource using a fake consumer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from stream_iterator.infrastructure.kafka_source import KafkaMessageSource


@dataclass
class FakeRecord:
    key: str | None
    value: dict[str, object]
    offset: int
    partition: int


class FakeConsumer:
    def __init__(self, records_by_partition: dict[Any, list[FakeRecord]]) -> None:
        self._records_by_partition = records_by_partition

    def poll(self, timeout_ms: int) -> dict[Any, list[FakeRecord]]:
        return self._records_by_partition


def test_poll_flattens_records_across_partitions() -> None:
    consumer = FakeConsumer(
        {
            "p0": [FakeRecord(key="a", value={"amount": 10}, offset=0, partition=0)],
            "p1": [FakeRecord(key="b", value={"amount": 5}, offset=0, partition=1)],
        }
    )
    source = KafkaMessageSource(consumer)

    messages = source.poll(timeout_ms=500)

    assert len(messages) == 2
    assert {m.partition for m in messages} == {0, 1}


def test_poll_returns_empty_list_when_nothing_available() -> None:
    source = KafkaMessageSource(FakeConsumer({}))

    assert source.poll(timeout_ms=500) == []


def test_poll_preserves_message_fields() -> None:
    consumer = FakeConsumer(
        {"p0": [FakeRecord(key="k1", value={"amount": 42}, offset=7, partition=0)]}
    )
    source = KafkaMessageSource(consumer)

    [message] = source.poll(timeout_ms=500)

    assert message.key == "k1"
    assert message.value == {"amount": 42}
    assert message.offset == 7
    assert message.partition == 0
