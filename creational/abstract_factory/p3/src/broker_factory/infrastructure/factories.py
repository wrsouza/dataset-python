"""Concrete Factories and Concrete Products for the Message Broker Factory.

Three broker families: RabbitMQ, Kafka, SQS (LocalStack).
Each family is self-contained — changing one never affects the others (OCP).

Note: pika (RabbitMQ) and kafka-python are optional runtime deps.
In unit tests, these factories are mocked; integration tests require the
docker-compose services to be running.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, cast

import boto3

from broker_factory.domain.interfaces import MessageBrokerFactory

# ── In-Memory Fake Products (used by unit tests and as fallback) ───────────────


class InMemoryProducer:
    """Fake Producer backed by an in-memory dict — no external dependencies."""

    def __init__(self, store: dict[str, list[str]], broker_name: str) -> None:
        self._store = store
        self._broker_name = broker_name

    def publish(self, destination: str, message: str) -> None:
        self._store[destination].append(message)

    def close(self) -> None:
        pass  # Nothing to release for in-memory store


class InMemoryConsumer:
    """Fake Consumer backed by an in-memory dict."""

    def __init__(self, store: dict[str, list[str]]) -> None:
        self._store = store

    def consume(self, source: str, max_messages: int) -> list[str]:
        messages = self._store.get(source, [])
        consumed = messages[:max_messages]
        self._store[source] = messages[max_messages:]
        return consumed

    def acknowledge(self, message_id: str) -> None:
        pass  # In-memory: no explicit ack needed

    def close(self) -> None:
        pass


class InMemoryQueueAdmin:
    """Fake QueueAdmin backed by an in-memory set."""

    def __init__(self, queues: set[str]) -> None:
        self._queues = queues

    def create_queue(self, name: str) -> str:
        self._queues.add(name)
        return f"in-memory://{name}"

    def delete_queue(self, name: str) -> None:
        self._queues.discard(name)

    def list_queues(self) -> list[str]:
        return sorted(self._queues)


# ── RabbitMQ Concrete Products ─────────────────────────────────────────────────


class RabbitMQProducer:
    """ConcreteProduct: publishes to RabbitMQ via pika."""

    def __init__(self, connection_url: str) -> None:
        self._url = connection_url
        self._connection: Any | None = None
        self._channel: Any | None = None
        self._connect()

    def _connect(self) -> None:
        import pika

        params = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()

    def publish(self, destination: str, message: str) -> None:
        assert self._channel is not None  # noqa: S101 - set in _connect()
        self._channel.queue_declare(queue=destination, durable=True)
        self._channel.basic_publish(
            exchange="",
            routing_key=destination,
            body=message.encode(),
        )

    def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            self._connection.close()


class RabbitMQConsumer:
    """ConcreteProduct: consumes from RabbitMQ via pika."""

    def __init__(self, connection_url: str) -> None:
        self._url = connection_url

    def consume(self, source: str, max_messages: int) -> list[str]:
        import pika

        params = pika.URLParameters(self._url)
        messages: list[str] = []
        with pika.BlockingConnection(params) as conn:
            channel = conn.channel()
            channel.queue_declare(queue=source, durable=True)
            for _ in range(max_messages):
                method, _props, body = channel.basic_get(source, auto_ack=True)
                if method is None:
                    break
                messages.append(body.decode())
        return messages

    def acknowledge(self, message_id: str) -> None:
        pass  # auto_ack=True handles this

    def close(self) -> None:
        pass


class RabbitMQQueueAdmin:
    """ConcreteProduct: manages RabbitMQ queues via pika."""

    def __init__(self, connection_url: str) -> None:
        self._url = connection_url

    def create_queue(self, name: str) -> str:
        import pika

        params = pika.URLParameters(self._url)
        with pika.BlockingConnection(params) as conn:
            conn.channel().queue_declare(queue=name, durable=True)
        return f"amqp://{name}"

    def delete_queue(self, name: str) -> None:
        import pika

        params = pika.URLParameters(self._url)
        with pika.BlockingConnection(params) as conn:
            conn.channel().queue_delete(queue=name)

    def list_queues(self) -> list[str]:
        # RabbitMQ management API would be needed for full listing
        # Returning empty list as placeholder — use management UI for full list
        return []


# ── Kafka Concrete Products ────────────────────────────────────────────────────


class KafkaProducer:
    """ConcreteProduct: publishes to Kafka via kafka-python."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._servers = bootstrap_servers
        self._producer = None

    def _get_producer(self) -> object:
        if self._producer is None:
            from kafka import KafkaProducer as KafkaPythonProducer

            self._producer = KafkaPythonProducer(
                bootstrap_servers=self._servers,
                value_serializer=lambda v: v.encode(),
            )
        return self._producer

    def publish(self, destination: str, message: str) -> None:
        producer = self._get_producer()
        producer.send(destination, message)  # type: ignore[attr-defined]
        producer.flush()  # type: ignore[attr-defined]

    def close(self) -> None:
        if self._producer:
            self._producer.close()
            self._producer = None


class KafkaConsumer:
    """ConcreteProduct: consumes from Kafka via kafka-python."""

    def __init__(
        self, bootstrap_servers: str, group_id: str = "broker-factory"
    ) -> None:
        self._servers = bootstrap_servers
        self._group_id = group_id
        self._consumer = None

    def consume(self, source: str, max_messages: int) -> list[str]:
        from kafka import KafkaConsumer as KafkaPythonConsumer

        consumer = KafkaPythonConsumer(
            source,
            bootstrap_servers=self._servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            consumer_timeout_ms=2000,
            value_deserializer=lambda v: v.decode(),
        )
        messages: list[str] = []
        for msg in consumer:
            messages.append(msg.value)
            if len(messages) >= max_messages:
                break
        consumer.close()
        return messages

    def acknowledge(self, message_id: str) -> None:
        pass  # Kafka uses offset commits — auto-commit handles this

    def close(self) -> None:
        if self._consumer:
            self._consumer.close()


class KafkaQueueAdmin:
    """ConcreteProduct: manages Kafka topics via kafka-python admin."""

    def __init__(self, bootstrap_servers: str) -> None:
        self._servers = bootstrap_servers

    def create_queue(self, name: str) -> str:
        from kafka.admin import KafkaAdminClient, NewTopic

        admin = KafkaAdminClient(bootstrap_servers=self._servers)
        topic = NewTopic(name=name, num_partitions=1, replication_factor=1)
        try:
            admin.create_topics([topic])
        except Exception as exc:  # noqa: BLE001 - topic may already exist
            logging.getLogger(__name__).debug(
                "Topic '%s' creation skipped: %s", name, exc
            )
        finally:
            admin.close()
        return f"kafka://{name}"

    def delete_queue(self, name: str) -> None:
        from kafka.admin import KafkaAdminClient

        admin = KafkaAdminClient(bootstrap_servers=self._servers)
        try:
            admin.delete_topics([name])
        finally:
            admin.close()

    def list_queues(self) -> list[str]:
        from kafka.admin import KafkaAdminClient

        admin = KafkaAdminClient(bootstrap_servers=self._servers)
        try:
            metadata = admin.list_topics()
            return [t for t in metadata if not t.startswith("__")]
        finally:
            admin.close()


# ── SQS Concrete Products (LocalStack) ────────────────────────────────────────


class SQSProducer:
    """ConcreteProduct: publishes to SQS via boto3 (LocalStack)."""

    def __init__(self, sqs_client: object) -> None:
        self._sqs = sqs_client

    def _get_queue_url(self, name: str) -> str:
        response = self._sqs.get_queue_url(QueueName=name)  # type: ignore[attr-defined]
        return cast(str, response["QueueUrl"])

    def publish(self, destination: str, message: str) -> None:
        queue_url = self._get_queue_url(destination)
        self._sqs.send_message(QueueUrl=queue_url, MessageBody=message)  # type: ignore[attr-defined]

    def close(self) -> None:
        pass  # boto3 client is stateless


class SQSConsumer:
    """ConcreteProduct: consumes from SQS via boto3 (LocalStack)."""

    def __init__(self, sqs_client: object) -> None:
        self._sqs = sqs_client

    def consume(self, source: str, max_messages: int) -> list[str]:
        response = self._sqs.get_queue_url(QueueName=source)  # type: ignore[attr-defined]
        queue_url = response["QueueUrl"]
        capped = min(max_messages, 10)  # SQS max per receive is 10
        response = self._sqs.receive_message(  # type: ignore[attr-defined]
            QueueUrl=queue_url,
            MaxNumberOfMessages=capped,
            WaitTimeSeconds=1,
        )
        messages_raw = response.get("Messages", [])
        results: list[str] = []
        for msg in messages_raw:
            results.append(msg["Body"])
            self._sqs.delete_message(  # type: ignore[attr-defined]
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )
        return results

    def acknowledge(self, message_id: str) -> None:
        pass  # SQS deletes messages on receive in consume()

    def close(self) -> None:
        pass


class SQSQueueAdmin:
    """ConcreteProduct: manages SQS queues via boto3 (LocalStack)."""

    def __init__(self, sqs_client: object) -> None:
        self._sqs = sqs_client

    def create_queue(self, name: str) -> str:
        response = self._sqs.create_queue(QueueName=name)  # type: ignore[attr-defined]
        return cast(str, response["QueueUrl"])

    def delete_queue(self, name: str) -> None:
        response = self._sqs.get_queue_url(QueueName=name)  # type: ignore[attr-defined]
        self._sqs.delete_queue(QueueUrl=response["QueueUrl"])  # type: ignore[attr-defined]

    def list_queues(self) -> list[str]:
        response = self._sqs.list_queues()  # type: ignore[attr-defined]
        urls = response.get("QueueUrls", [])
        return [url.split("/")[-1] for url in urls]


# ── Concrete Factories ─────────────────────────────────────────────────────────


class InMemoryBrokerFactory(MessageBrokerFactory):
    """ConcreteFactory: in-memory broker for unit testing — no external services."""

    def __init__(self, broker_name: str = "in-memory") -> None:
        self._store: dict[str, list[str]] = defaultdict(list)
        self._queues: set[str] = set()
        self._broker_name = broker_name

    def create_producer(self) -> InMemoryProducer:
        return InMemoryProducer(self._store, self._broker_name)

    def create_consumer(self) -> InMemoryConsumer:
        return InMemoryConsumer(self._store)

    def create_admin(self) -> InMemoryQueueAdmin:
        return InMemoryQueueAdmin(self._queues)

    def get_broker_name(self) -> str:
        return self._broker_name


class RabbitMQFactory(MessageBrokerFactory):
    """ConcreteFactory: creates the RabbitMQ product family."""

    def __init__(
        self,
        connection_url: str = "amqp://app:secret@rabbitmq:5672/",
    ) -> None:
        self._url = connection_url

    def create_producer(self) -> RabbitMQProducer:
        return RabbitMQProducer(self._url)

    def create_consumer(self) -> RabbitMQConsumer:
        return RabbitMQConsumer(self._url)

    def create_admin(self) -> RabbitMQQueueAdmin:
        return RabbitMQQueueAdmin(self._url)

    def get_broker_name(self) -> str:
        return "rabbitmq"


class KafkaFactory(MessageBrokerFactory):
    """ConcreteFactory: creates the Kafka product family."""

    def __init__(self, bootstrap_servers: str = "kafka:9092") -> None:
        self._bootstrap_servers = bootstrap_servers

    def create_producer(self) -> KafkaProducer:
        return KafkaProducer(self._bootstrap_servers)

    def create_consumer(self) -> KafkaConsumer:
        return KafkaConsumer(self._bootstrap_servers)

    def create_admin(self) -> KafkaQueueAdmin:
        return KafkaQueueAdmin(self._bootstrap_servers)

    def get_broker_name(self) -> str:
        return "kafka"


class SQSFactory(MessageBrokerFactory):
    """ConcreteFactory: creates the SQS product family (uses LocalStack)."""

    def __init__(
        self,
        endpoint_url: str = "http://localstack:4566",
        region: str = "us-east-1",
    ) -> None:
        self._endpoint_url = endpoint_url
        self._region = region

    def _build_sqs_client(self) -> object:
        # LocalStack accepts any non-empty credentials — these are not real
        # AWS secrets, just placeholders required by the boto3 client API.
        return boto3.client(
            "sqs",
            endpoint_url=self._endpoint_url,
            region_name=self._region,
            aws_access_key_id="test",  # noqa: S106
            aws_secret_access_key="test",  # noqa: S106
        )

    def create_producer(self) -> SQSProducer:
        return SQSProducer(self._build_sqs_client())

    def create_consumer(self) -> SQSConsumer:
        return SQSConsumer(self._build_sqs_client())

    def create_admin(self) -> SQSQueueAdmin:
        return SQSQueueAdmin(self._build_sqs_client())

    def get_broker_name(self) -> str:
        return "sqs"


# ── Factory Registry ───────────────────────────────────────────────────────────


def build_broker_factory(
    broker: str,
    rabbitmq_url: str = "amqp://app:secret@rabbitmq:5672/",
    kafka_servers: str = "kafka:9092",
    localstack_url: str = "http://localstack:4566",
) -> MessageBrokerFactory:
    """Return the MessageBrokerFactory for the given broker name.

    OCP: register new brokers by adding entries here.
    """
    broker_map: dict[str, MessageBrokerFactory] = {
        "rabbitmq": RabbitMQFactory(connection_url=rabbitmq_url),
        "kafka": KafkaFactory(bootstrap_servers=kafka_servers),
        "sqs": SQSFactory(endpoint_url=localstack_url),
    }
    factory = broker_map.get(broker.lower())
    if factory is None:
        supported = ", ".join(broker_map.keys())
        raise ValueError(f"Unknown broker '{broker}'. Supported: {supported}")
    return factory
