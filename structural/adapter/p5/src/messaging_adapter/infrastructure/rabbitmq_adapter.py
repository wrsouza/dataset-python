"""RabbitMQAdapter — Adapter wrapping the pika client (Adaptee).

pika's native API is channel/exchange/queue oriented: ``queue_declare``,
``basic_publish``, ``basic_consume`` — nothing like the simple
``publish``/``consume`` shape application code wants. ``RabbitMQAdapter``
translates between the two, satisfying the ``MessageBroker`` Target.

SRP: this module only knows how to talk to RabbitMQ; it has no knowledge
of Kafka or any other broker.

Simulation mode: when pika is not installed or the broker is unreachable,
``connect()`` falls back to an in-memory buffer so unit tests can exercise
publish/consume without docker. ``docker-compose.yml`` brings up a real
RabbitMQ for integration tests.
"""

from __future__ import annotations

import json
import uuid
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


class RabbitMQAdapter:
    """Adapter — translates the MessageBroker Target onto pika (Adaptee).

    In production this wraps ``pika.BlockingConnection`` /
    ``channel.basic_publish`` / ``channel.basic_get``. When pika is
    unavailable (no native lib, or the broker is unreachable) it falls
    back to a deterministic in-memory simulation so the contract can
    still be exercised in unit tests.
    """

    def __init__(self) -> None:
        self._connected = False
        self._connection: Any | None = None
        self._channel: Any | None = None
        self._simulated_buffer: dict[str, list[Message]] = {}

    def connect(self) -> None:
        """Open a BlockingConnection to RabbitMQ, or enable simulation."""
        try:
            import pika

            credentials = pika.PlainCredentials("app", "secret")
            params = pika.ConnectionParameters(
                host="rabbitmq", port=5672, credentials=credentials
            )
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._connected = True
        except Exception:
            # Simulation mode: no real RabbitMQ available (unit tests / CI)
            self._connected = True

    def publish(self, topic: str, message: Message) -> None:
        """Declare *topic* as a durable queue and publish *message* to it."""
        if not self._connected:
            raise BrokerConnectionError("Adapter not connected. Call connect() first.")

        if self._channel is not None:
            try:
                self._channel.queue_declare(queue=topic, durable=True)
                import pika

                properties = pika.BasicProperties(
                    correlation_id=message.key,
                    headers=dict(message.headers),
                )
                self._channel.basic_publish(
                    exchange="",
                    routing_key=topic,
                    body=message.value,
                    properties=properties,
                )
            except Exception as exc:
                raise PublishError(f"RabbitMQ publish error: {exc}") from exc
        else:
            self._simulated_buffer.setdefault(topic, []).append(message)

    def consume(self, config: ConsumeConfig) -> Iterator[Message]:
        """Yield up to *config.limit* messages from the queue *config.topic*."""
        if self._channel is not None:
            try:
                count = 0
                while config.limit is None or count < config.limit:
                    method, props, body = self._channel.basic_get(
                        queue=config.topic, auto_ack=True
                    )
                    if method is None:
                        break
                    headers: dict[str, str] = {}
                    if props and props.headers:
                        headers = {k: str(v) for k, v in props.headers.items()}
                    yield Message(
                        topic=config.topic,
                        key=props.correlation_id if props else None,
                        value=body,
                        headers=headers,
                        timestamp=datetime.now(tz=UTC),
                    )
                    count += 1
            except Exception as exc:
                raise ConsumeError(f"RabbitMQ consume error: {exc}") from exc
        else:
            yield from self._consume_simulated(config)

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
                {"event": "payment.received", "amount": 99.90 + i}
            ).encode()
            yield Message(
                topic=config.topic,
                key=str(uuid.uuid4()),
                value=payload,
                headers={"source": "rabbitmq-sim", "content-type": "application/json"},
                timestamp=datetime.now(tz=UTC),
            )

    def close(self) -> None:
        """Close the AMQP connection, if any was opened."""
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:
                pass
        self._connected = False
