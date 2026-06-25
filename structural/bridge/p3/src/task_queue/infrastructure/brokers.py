"""ConcreteImplementors: broker drivers for the Queue Bridge pattern.

Three brokers: Celery/Redis, RabbitMQ (pika), SQS (boto3).
Each driver implements MessageBroker independently — adding a fourth
broker (Kafka, Google Pub/Sub, ...) means a new class here, with zero
changes to QueueClient subclasses or to the application layer (OCP).
"""

from __future__ import annotations

import json
import os
from collections import deque
from typing import ClassVar

from task_queue.domain.entities import (
    BrokerConnectionError,
    BrokerHealth,
    BrokerPublishError,
    QueueMessage,
)
from task_queue.domain.interfaces import MessageBroker

# ── Celery / Redis ──────────────────────────────────────────────────────────


class CeleryRedisBroker(MessageBroker):
    """ConcreteImplementor: publishes/consumes via Celery backed by Redis.

    Uses Redis lists directly (LPUSH/RPOP) as a lightweight stand-in for a
    full Celery worker pool — this keeps the teaching example runnable
    without spinning up Celery workers, while still exercising the same
    Redis connection a Celery app would use as its broker.
    """

    def __init__(self) -> None:
        self._redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self._client: object | None = None

    def _get_client(self) -> object:
        if self._client is None:
            import redis

            self._client = redis.Redis.from_url(self._redis_url)
        return self._client

    def publish(self, message: QueueMessage) -> str:
        try:
            client = self._get_client()
            client.lpush(message.queue_name, json.dumps(message.to_dict()))  # type: ignore[attr-defined]
            return message.message_id
        except Exception as exc:
            raise BrokerPublishError("CeleryRedis", str(exc)) from exc

    def consume(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        try:
            client = self._get_client()
            messages: list[QueueMessage] = []
            for _ in range(max_messages):
                raw = client.rpop(queue_name)  # type: ignore[attr-defined]
                if raw is None:
                    break
                data = json.loads(raw)
                messages.append(
                    QueueMessage(
                        queue_name=data["queue_name"],
                        payload=data["payload"],
                        message_id=data["message_id"],
                    )
                )
            return messages
        except Exception as exc:
            raise BrokerConnectionError("CeleryRedis", str(exc)) from exc

    def acknowledge(self, message_id: str) -> bool:
        # Redis list pop is already destructive (RPOP removes the item),
        # so acknowledgement is implicit. Kept for interface compliance.
        return True

    def health_check(self) -> BrokerHealth:
        try:
            client = self._get_client()
            pong = client.ping()  # type: ignore[attr-defined]
            return BrokerHealth(
                broker="CeleryRedis",
                is_healthy=bool(pong),
                details={"redis_url": self._redact(self._redis_url)},
            )
        except Exception as exc:  # noqa: BLE001
            return BrokerHealth(
                broker="CeleryRedis",
                is_healthy=False,
                error_message=str(exc),
            )

    def get_broker_name(self) -> str:
        return "CeleryRedis"

    @staticmethod
    def _redact(url: str) -> str:
        return url.split("@")[-1] if "@" in url else url


# ── RabbitMQ (pika) ──────────────────────────────────────────────────────────


class RabbitMQBroker(MessageBroker):
    """ConcreteImplementor: publishes/consumes via RabbitMQ using pika."""

    def __init__(self) -> None:
        self._host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self._port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self._user = os.getenv("RABBITMQ_USER", "guest")
        self._password = os.getenv("RABBITMQ_PASSWORD", "guest")

    def _connect(self) -> object:
        import pika

        credentials = pika.PlainCredentials(self._user, self._password)
        params = pika.ConnectionParameters(
            host=self._host,
            port=self._port,
            credentials=credentials,
            connection_attempts=1,
            socket_timeout=3,
        )
        return pika.BlockingConnection(params)

    def publish(self, message: QueueMessage) -> str:
        try:
            connection = self._connect()
            channel = connection.channel()  # type: ignore[attr-defined]
            channel.queue_declare(queue=message.queue_name, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=message.queue_name,
                body=json.dumps(message.to_dict()),
            )
            connection.close()  # type: ignore[attr-defined]
            return message.message_id
        except Exception as exc:
            raise BrokerPublishError("RabbitMQ", str(exc)) from exc

    def consume(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        try:
            connection = self._connect()
            channel = connection.channel()  # type: ignore[attr-defined]
            channel.queue_declare(queue=queue_name, durable=True)
            messages: list[QueueMessage] = []
            for _ in range(max_messages):
                method, _properties, body = channel.basic_get(
                    queue=queue_name, auto_ack=True
                )
                if method is None or body is None:
                    break
                data = json.loads(body)
                messages.append(
                    QueueMessage(
                        queue_name=data["queue_name"],
                        payload=data["payload"],
                        message_id=data["message_id"],
                    )
                )
            connection.close()  # type: ignore[attr-defined]
            return messages
        except Exception as exc:
            raise BrokerConnectionError("RabbitMQ", str(exc)) from exc

    def acknowledge(self, message_id: str) -> bool:
        # basic_get(auto_ack=True) already acknowledges on delivery.
        return True

    def health_check(self) -> BrokerHealth:
        try:
            connection = self._connect()
            is_open = bool(connection.is_open)  # type: ignore[attr-defined]
            connection.close()  # type: ignore[attr-defined]
            return BrokerHealth(
                broker="RabbitMQ",
                is_healthy=is_open,
                details={"host": self._host, "port": str(self._port)},
            )
        except Exception as exc:  # noqa: BLE001
            return BrokerHealth(
                broker="RabbitMQ",
                is_healthy=False,
                error_message=str(exc),
            )

    def get_broker_name(self) -> str:
        return "RabbitMQ"


# ── SQS (boto3) ──────────────────────────────────────────────────────────────


class SQSBroker(MessageBroker):
    """ConcreteImplementor: publishes/consumes via AWS SQS using boto3.

    Points at LocalStack by default (AWS_ENDPOINT_URL) so the teaching
    example never touches real AWS infrastructure.
    """

    _queue_urls: ClassVar[dict[str, str]] = {}

    def __init__(self) -> None:
        self._endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
        self._region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self._client: object | None = None

    def _get_client(self) -> object:
        if self._client is None:
            import boto3

            self._client = boto3.client(
                "sqs",
                endpoint_url=self._endpoint_url,
                region_name=self._region,
            )
        return self._client

    def _get_queue_url(self, queue_name: str) -> str:
        if queue_name not in self._queue_urls:
            client = self._get_client()
            try:
                response = client.get_queue_url(QueueName=queue_name)  # type: ignore[attr-defined]
                url = response["QueueUrl"]
            except Exception:
                response = client.create_queue(QueueName=queue_name)  # type: ignore[attr-defined]
                url = response["QueueUrl"]
            self._queue_urls[queue_name] = url
        return self._queue_urls[queue_name]

    def publish(self, message: QueueMessage) -> str:
        try:
            client = self._get_client()
            queue_url = self._get_queue_url(message.queue_name)
            client.send_message(  # type: ignore[attr-defined]
                QueueUrl=queue_url,
                MessageBody=json.dumps(message.to_dict()),
            )
            return message.message_id
        except Exception as exc:
            raise BrokerPublishError("SQS", str(exc)) from exc

    def consume(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        try:
            client = self._get_client()
            queue_url = self._get_queue_url(queue_name)
            response = client.receive_message(  # type: ignore[attr-defined]
                QueueUrl=queue_url,
                MaxNumberOfMessages=min(max_messages, 10),
            )
            raw_messages = response.get("Messages", [])
            messages: list[QueueMessage] = []
            for raw in raw_messages:
                data = json.loads(raw["Body"])
                messages.append(
                    QueueMessage(
                        queue_name=data["queue_name"],
                        payload=data["payload"],
                        message_id=data["message_id"],
                    )
                )
                client.delete_message(  # type: ignore[attr-defined]
                    QueueUrl=queue_url,
                    ReceiptHandle=raw["ReceiptHandle"],
                )
            return messages
        except Exception as exc:
            raise BrokerConnectionError("SQS", str(exc)) from exc

    def acknowledge(self, message_id: str) -> bool:
        # delete_message() in consume() already acknowledges receipt.
        return True

    def health_check(self) -> BrokerHealth:
        try:
            client = self._get_client()
            client.list_queues()  # type: ignore[attr-defined]
            return BrokerHealth(
                broker="SQS",
                is_healthy=True,
                details={"endpoint_url": self._endpoint_url, "region": self._region},
            )
        except Exception as exc:  # noqa: BLE001
            return BrokerHealth(
                broker="SQS",
                is_healthy=False,
                error_message=str(exc),
            )

    def get_broker_name(self) -> str:
        return "SQS"


# ── In-memory broker (deterministic fallback for local teaching/demo) ──────


class InMemoryBroker(MessageBroker):
    """ConcreteImplementor: pure in-process broker, no external services.

    Not part of the three required brokers, but useful as a safe default
    and for exercising the Bridge without any infrastructure dependency.
    """

    def __init__(self) -> None:
        self._queues: dict[str, deque[QueueMessage]] = {}

    def publish(self, message: QueueMessage) -> str:
        self._queues.setdefault(message.queue_name, deque()).append(message)
        return message.message_id

    def consume(self, queue_name: str, max_messages: int = 1) -> list[QueueMessage]:
        queue = self._queues.get(queue_name, deque())
        messages = []
        for _ in range(max_messages):
            if not queue:
                break
            messages.append(queue.popleft())
        return messages

    def acknowledge(self, message_id: str) -> bool:
        return True

    def health_check(self) -> BrokerHealth:
        return BrokerHealth(broker="InMemory", is_healthy=True, details={})

    def get_broker_name(self) -> str:
        return "InMemory"


# ── Broker Registry ─────────────────────────────────────────────────────────

BROKER_REGISTRY: dict[str, type[MessageBroker]] = {
    "celery_redis": CeleryRedisBroker,
    "rabbitmq": RabbitMQBroker,
    "sqs": SQSBroker,
    "memory": InMemoryBroker,
}


def get_broker(broker_type: str) -> MessageBroker:
    """Instantiate the MessageBroker for the given identifier.

    OCP: registering a new broker only requires an entry in BROKER_REGISTRY.
    No if/elif chains scattered across views or use cases.
    """
    broker_cls = BROKER_REGISTRY.get(broker_type.lower())
    if broker_cls is None:
        supported = ", ".join(BROKER_REGISTRY.keys())
        raise ValueError(
            f"Unsupported broker type '{broker_type}'. Supported: {supported}"
        )
    return broker_cls()
