"""KafkaAdapter — Adapter wrapping the kafka-python client (Adaptee).

kafka-python exposes ``KafkaProducer.send`` / ``KafkaConsumer.poll`` —
partition- and offset-aware, with futures and record batches. None of
that shape is exposed to application code: ``KafkaAdapter`` translates
calls to/from the plain ``MessageBroker`` Target.

SRP: this module only knows how to talk to Kafka. OCP: adding a third
broker (e.g. SQS) means adding a new adapter module here, with zero
changes to this file, ``RabbitMQAdapter``, or the ``MessageBroker``
Protocol.

Simulation mode: when kafka-python is not installed or the cluster is
unreachable, ``connect()`` falls back to an in-memory buffer so unit
tests can exercise publish/consume without docker. Connection checks use
a short, bounded timeout (``_CONNECT_TIMEOUT_MS``) so falling back to
simulation never blocks the caller for long.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

from messaging_adapter.domain.entities import (
    BrokerConnectionError,
    ConsumeConfig,
    ConsumeError,
    Message,
    PublishError,
)

_BOOTSTRAP_SERVERS = ["kafka:9092"]
_CONNECT_TIMEOUT_MS = 1000


class KafkaAdapter:
    """Adapter — translates the MessageBroker Target onto kafka-python (Adaptee).

    In production this wraps ``kafka.KafkaProducer.send`` and
    ``kafka.KafkaConsumer.poll``. Falls back to a deterministic in-memory
    simulation when kafka-python is unavailable.
    """

    def __init__(self) -> None:
        self._connected = False
        self._producer: Any | None = None
        self._consumer: Any | None = None
        self._simulated_buffer: dict[str, list[Message]] = {}

    def connect(self) -> None:
        """Create a KafkaProducer, or enable simulation if unreachable.

        ``request_timeout_ms``/``max_block_ms`` bound how long the
        connection attempt can take, so falling back to simulation mode
        is fast even when the configured broker host cannot be resolved.
        A lightweight ``bootstrap_connected()`` probe forces kafka-python
        to attempt the connection eagerly instead of lazily on first send.
        """
        try:
            import kafka

            producer = kafka.KafkaProducer(
                bootstrap_servers=_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: v,
                api_version=(2, 5, 0),
                request_timeout_ms=_CONNECT_TIMEOUT_MS,
                max_block_ms=_CONNECT_TIMEOUT_MS,
            )
            if not producer.bootstrap_connected():
                producer.close(timeout=_CONNECT_TIMEOUT_MS / 1000)
                raise BrokerConnectionError("Kafka bootstrap unreachable")
            self._producer = producer
            self._connected = True
        except Exception:
            # Simulation mode: no real Kafka available (unit tests / CI)
            self._connected = True

    def publish(self, topic: str, message: Message) -> None:
        """Send *message* to the Kafka *topic* via the producer."""
        if not self._connected:
            raise BrokerConnectionError("Adapter not connected. Call connect() first.")

        if self._producer is not None:
            try:
                key = message.key.encode() if message.key else None
                headers = [(k, v.encode()) for k, v in message.headers.items()]
                future = self._producer.send(
                    topic, value=message.value, key=key, headers=headers
                )
                future.get(timeout=_CONNECT_TIMEOUT_MS / 1000)
            except Exception as exc:
                raise PublishError(f"Kafka publish error: {exc}") from exc
        else:
            self._simulated_buffer.setdefault(topic, []).append(message)

    def consume(self, config: ConsumeConfig) -> Iterator[Message]:
        """Yield up to *config.limit* messages from *config.topic*."""
        if self._producer is not None:
            yield from self._consume_real(config)
        else:
            yield from self._consume_simulated(config)

    def _consume_real(self, config: ConsumeConfig) -> Iterator[Message]:
        """Poll a short-lived KafkaConsumer for available records."""
        try:
            import kafka

            consumer = kafka.KafkaConsumer(
                config.topic,
                bootstrap_servers=_BOOTSTRAP_SERVERS,
                group_id=config.group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                api_version=(2, 5, 0),
                consumer_timeout_ms=int(config.timeout_seconds * 1000),
            )
            self._consumer = consumer
            count = 0
            for record in consumer:
                if config.limit is not None and count >= config.limit:
                    break
                yield Message(
                    topic=record.topic,
                    key=record.key.decode() if record.key else None,
                    value=record.value,
                    headers={k: v.decode() for k, v in (record.headers or [])},
                    timestamp=datetime.fromtimestamp(record.timestamp / 1000, tz=UTC),
                )
                count += 1
            consumer.close()
        except Exception as exc:
            raise ConsumeError(f"Kafka consume error: {exc}") from exc

    def _consume_simulated(self, config: ConsumeConfig) -> Iterator[Message]:
        """Replay buffered messages, generating deterministic ones if empty."""
        buffered = self._simulated_buffer.get(config.topic, [])
        if buffered:
            limit = config.limit if config.limit is not None else len(buffered)
            yield from buffered[:limit]
            return

        limit = config.limit or 3
        for i in range(limit):
            payload = json.dumps(
                {"event": "order.created", "order_id": f"ORD-{1000 + i}"}
            ).encode()
            yield Message(
                topic=config.topic,
                key=f"key-{i}",
                value=payload,
                headers={"source": "kafka-sim"},
                timestamp=datetime.now(tz=UTC),
            )

    def close(self) -> None:
        """Flush and close the producer/consumer, if any were opened."""
        if self._producer is not None:
            try:
                self._producer.close(timeout=_CONNECT_TIMEOUT_MS / 1000)
            except Exception:
                pass
        if self._consumer is not None:
            try:
                self._consumer.close()
            except Exception:
                pass
        self._connected = False
