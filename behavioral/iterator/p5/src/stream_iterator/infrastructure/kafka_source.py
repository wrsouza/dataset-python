"""Kafka-backed implementation of MessageSource, built on kafka-python."""

from __future__ import annotations

from typing import Any, Protocol

from stream_iterator.domain.entities import StreamMessage
from stream_iterator.domain.interfaces import MessageSource


class KafkaConsumerLike(Protocol):
    """Minimal kafka-python KafkaConsumer contract this source relies on."""

    def poll(self, timeout_ms: int) -> dict[Any, list[Any]]: ...


class KafkaMessageSource(MessageSource):
    """Polls a Kafka topic via a kafka-python consumer's `poll()` API."""

    def __init__(self, consumer: KafkaConsumerLike) -> None:
        self._consumer = consumer

    def poll(self, timeout_ms: int) -> list[StreamMessage]:
        records_by_partition = self._consumer.poll(timeout_ms=timeout_ms)
        messages: list[StreamMessage] = []
        for records in records_by_partition.values():
            for record in records:
                messages.append(
                    StreamMessage(
                        key=record.key,
                        value=record.value,
                        offset=record.offset,
                        partition=record.partition,
                    )
                )
        return messages
