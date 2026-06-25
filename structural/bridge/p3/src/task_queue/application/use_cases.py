"""Application use cases for the Queue Bridge.

All use cases depend on QueueClient (abstraction) — never on a concrete
broker. This keeps the application layer Bridge-agnostic: swapping
Celery/Redis for RabbitMQ or SQS requires no changes here.
"""

from __future__ import annotations

from task_queue.domain.entities import BrokerHealth, DequeueResult, EnqueueResult
from task_queue.domain.interfaces import QueueClient


class EnqueueMessageUseCase:
    """Publishes a message onto a queue via the injected QueueClient.

    DIP: receives QueueClient via constructor.
    SRP: enqueueing only — no dequeue, no health check.
    """

    def __init__(self, client: QueueClient) -> None:
        self._client = client

    def execute(self, payload: dict[str, object], queue_name: str) -> EnqueueResult:
        message_id = self._client.enqueue(payload, queue_name)
        return EnqueueResult(
            broker=self._client.get_broker_name(),
            queue_name=queue_name,
            message_id=message_id,
        )


class DequeueMessagesUseCase:
    """Retrieves pending messages from a queue via the injected QueueClient.

    DIP: depends on QueueClient, not on kombu/pika/boto3.
    SRP: dequeue only.
    """

    def __init__(self, client: QueueClient) -> None:
        self._client = client

    def execute(self, queue_name: str, max_messages: int = 1) -> DequeueResult:
        messages = self._client.dequeue(queue_name, max_messages=max_messages)
        return DequeueResult(
            broker=self._client.get_broker_name(),
            queue_name=queue_name,
            messages=[m.to_dict() for m in messages],
            message_count=len(messages),
        )


class CheckBrokerHealthUseCase:
    """Checks whether the broker behind a QueueClient is reachable.

    DIP: receives QueueClient via constructor.
    SRP: health check only.
    """

    def __init__(self, client: QueueClient) -> None:
        self._client = client

    def execute(self) -> BrokerHealth:
        """Never raises — broker-level failures are represented as
        is_healthy=False so HTTP views always return a structured response.
        """
        try:
            return self._client.check_health()
        except Exception as exc:  # noqa: BLE001 — health check must not 500
            return BrokerHealth(
                broker=self._client.get_broker_name(),
                is_healthy=False,
                error_message=str(exc),
            )
