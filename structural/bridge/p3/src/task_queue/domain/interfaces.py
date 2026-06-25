"""Abstract interfaces for the Queue Bridge pattern.

Bridge structure:
    Abstraction        -> QueueClient
    RefinedAbstraction  -> TaskQueueClient, PriorityQueueClient
    Implementor         -> MessageBroker
    ConcreteImplementor -> CeleryRedisBroker, RabbitMQBroker, SQSBroker

SRP: QueueClient knows WHAT to do with a message (task semantics, priority
     semantics); MessageBroker knows HOW to talk to the underlying transport.
OCP: new broker = new MessageBroker subclass, zero changes to QueueClient
     subclasses or to the application layer.
DIP: QueueClient depends on the MessageBroker abstraction, never on a
     concrete broker class.
ISP: MessageBroker exposes only the small surface every broker needs
     (publish/consume/ack/health) — no broker-specific methods leak in.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_queue.domain.entities import BrokerHealth, QueueMessage


class MessageBroker(ABC):
    """Implementor: the contract every concrete broker driver must satisfy.

    ISP: this interface is intentionally small. Clients that only need to
    publish never need to know about consume/ack.
    """

    @abstractmethod
    def publish(self, message: QueueMessage) -> str:
        """Publish a message to the broker and return a broker-assigned id."""
        ...

    @abstractmethod
    def consume(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        """Pull up to ``max_messages`` messages from ``queue_name``."""
        ...

    @abstractmethod
    def acknowledge(self, message_id: str) -> bool:
        """Acknowledge successful processing of a message. Returns success."""
        ...

    @abstractmethod
    def health_check(self) -> BrokerHealth:
        """Return the current health/connectivity status of the broker."""
        ...

    @abstractmethod
    def get_broker_name(self) -> str:
        """Return the human-readable broker name (for logging/telemetry)."""
        ...


class QueueClient(ABC):
    """Abstraction: defines queueing semantics, delegating transport to a
    MessageBroker (Implementor) received via composition.

    DIP: stores a MessageBroker reference, never a concrete broker class.
    """

    def __init__(self, broker: MessageBroker) -> None:
        self._broker = broker

    @abstractmethod
    def enqueue(self, payload: dict[str, object], queue_name: str) -> str:
        """Build a QueueMessage from payload and submit it to the broker."""
        ...

    @abstractmethod
    def dequeue(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        """Retrieve pending messages for the given queue."""
        ...

    def get_broker_name(self) -> str:
        """Expose the underlying broker's name without leaking its type."""
        return self._broker.get_broker_name()

    def check_health(self) -> BrokerHealth:
        """Delegate health checking to the underlying broker."""
        return self._broker.health_check()
