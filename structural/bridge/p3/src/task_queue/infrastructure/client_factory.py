"""Factory helpers wiring RefinedAbstractions to ConcreteImplementors.

Kept separate from brokers.py: this module is the only place that knows
about both QueueClient subclasses and MessageBroker subclasses at once,
acting as the Bridge's composition root.
"""

from __future__ import annotations

from task_queue.domain.interfaces import QueueClient
from task_queue.domain.queue_clients import PriorityQueueClient, TaskQueueClient
from task_queue.infrastructure.brokers import get_broker

CLIENT_REGISTRY: dict[str, type[QueueClient]] = {
    "task": TaskQueueClient,
    "priority": PriorityQueueClient,
}


def build_queue_client(client_type: str, broker_type: str) -> QueueClient:
    """Build a fully wired QueueClient for the given client/broker pair.

    OCP: new client semantics or new brokers only require registry entries.
    DIP: callers (Django views) receive a QueueClient — they never import
    TaskQueueClient, CeleryRedisBroker, etc. directly in business logic.
    """
    client_cls = CLIENT_REGISTRY.get(client_type.lower())
    if client_cls is None:
        supported = ", ".join(CLIENT_REGISTRY.keys())
        raise ValueError(
            f"Unsupported client type '{client_type}'. Supported: {supported}"
        )
    broker = get_broker(broker_type)
    return client_cls(broker)
