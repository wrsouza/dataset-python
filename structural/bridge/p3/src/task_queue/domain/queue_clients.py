"""RefinedAbstractions for the Queue Bridge pattern.

Each QueueClient subclass defines queueing semantics (what a message means,
how priority is handled) while delegating all transport concerns to the
MessageBroker (Implementor) it was constructed with.
"""

from __future__ import annotations

from task_queue.domain.entities import MessagePriority, QueueMessage
from task_queue.domain.interfaces import MessageBroker, QueueClient


class TaskQueueClient(QueueClient):
    """RefinedAbstraction: simple fire-and-forget task queue semantics.

    SRP: only knows how to wrap a payload into a NORMAL-priority QueueMessage
    and hand it to the broker — no priority logic, no retries.
    """

    def enqueue(self, payload: dict[str, object], queue_name: str) -> str:
        message = QueueMessage(
            queue_name=queue_name,
            payload=payload,
            priority=MessagePriority.NORMAL,
        )
        return self._broker.publish(message)

    def dequeue(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        return self._broker.consume(queue_name, max_messages=max_messages)


class PriorityQueueClient(QueueClient):
    """RefinedAbstraction: priority-aware queue semantics.

    SRP: extracts a 'priority' hint from the payload and stamps the
    QueueMessage accordingly — still oblivious to which broker delivers it.
    """

    def __init__(
        self,
        broker: MessageBroker,
        default_priority: MessagePriority = MessagePriority.NORMAL,
    ) -> None:
        super().__init__(broker)
        self._default_priority = default_priority

    def enqueue(self, payload: dict[str, object], queue_name: str) -> str:
        priority = self._resolve_priority(payload)
        message = QueueMessage(
            queue_name=queue_name,
            payload=payload,
            priority=priority,
        )
        return self._broker.publish(message)

    def dequeue(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        return self._broker.consume(queue_name, max_messages=max_messages)

    def _resolve_priority(self, payload: dict[str, object]) -> MessagePriority:
        raw = payload.get("priority")
        if isinstance(raw, str):
            try:
                return MessagePriority(raw.lower())
            except ValueError:
                return self._default_priority
        return self._default_priority
