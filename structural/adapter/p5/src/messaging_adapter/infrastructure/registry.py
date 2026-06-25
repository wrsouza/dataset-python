"""Broker registry — OCP-friendly Adapter selection.

Adding a new broker (e.g. SQS) means writing a new ``SQSAdapter`` class
and adding one entry to ``BROKER_REGISTRY``. No existing Adapter, the
``MessageBroker`` Protocol, the use cases, or the CLI need to change.
"""

from __future__ import annotations

from messaging_adapter.domain.entities import BrokerType
from messaging_adapter.domain.interfaces import MessageBroker
from messaging_adapter.infrastructure.kafka_adapter import KafkaAdapter
from messaging_adapter.infrastructure.rabbitmq_adapter import RabbitMQAdapter


def build_broker_registry() -> dict[BrokerType, MessageBroker]:
    """Construct a fresh registry mapping BrokerType to a MessageBroker.

    A factory function (rather than a module-level singleton dict) is
    used so each caller — and each test — gets independent Adapter
    instances with their own connection state.
    """
    return {
        BrokerType.RABBITMQ: RabbitMQAdapter(),
        BrokerType.KAFKA: KafkaAdapter(),
    }


BROKER_DISPLAY_NAMES: dict[BrokerType, str] = {
    BrokerType.RABBITMQ: "RabbitMQ",
    BrokerType.KAFKA: "Kafka",
}
