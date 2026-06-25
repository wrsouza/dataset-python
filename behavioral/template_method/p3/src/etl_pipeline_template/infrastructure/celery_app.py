"""Celery application instance and the ETL-completion publish task."""

from __future__ import annotations

import os

from celery import Celery

from etl_pipeline_template.infrastructure.kafka_publisher import (
    KafkaEtlEventPublisher,
    KafkaProducerLike,
)

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

app = Celery(
    "etl_pipeline_template",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
app.conf.task_track_started = True
app.conf.task_always_eager = (
    os.environ.get("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
)
app.conf.task_eager_propagates = app.conf.task_always_eager


def build_kafka_producer() -> KafkaProducerLike:
    from kafka import KafkaProducer

    producer: KafkaProducerLike = KafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    )
    return producer


@app.task(name="etl_pipeline_template.publish_completion")  # type: ignore[untyped-decorator]
def publish_etl_completion_task(pipeline_name: str, records_loaded: int) -> None:
    """Publish a `{pipeline_name, records_loaded}` event to Kafka.

    This is the Celery boundary: the ETLPipeline template method never
    talks to Kafka or Celery directly, it just calls `.delay()` on this
    task — what happens here (which producer, which topic) is an
    infrastructure concern.
    """
    topic = os.environ.get("KAFKA_TOPIC", "etl-events")
    publisher = KafkaEtlEventPublisher(build_kafka_producer(), topic)
    publisher.publish_completion(pipeline_name, records_loaded)
