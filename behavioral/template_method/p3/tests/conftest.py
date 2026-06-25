"""Shared pytest fixtures for the ETL Pipeline Template tests.

`CELERY_TASK_ALWAYS_EAGER` (set in config.settings_test) makes
`publish_etl_completion_task.delay()` run synchronously in-process. To
keep that from trying to reach a real Kafka broker, `build_kafka_producer`
is monkeypatched for every test to return a `FakeKafkaProducer` instead.
"""

from __future__ import annotations

import pytest

from etl_pipeline_template.infrastructure import celery_app


class FakeKafkaProducer:
    def __init__(self) -> None:
        self.sent: list[tuple[str, bytes]] = []

    def send(self, topic: str, value: bytes) -> object:
        self.sent.append((topic, value))
        return object()

    def flush(self) -> None:
        pass


@pytest.fixture(autouse=True)
def fake_kafka_producer(monkeypatch: pytest.MonkeyPatch) -> FakeKafkaProducer:
    producer = FakeKafkaProducer()
    monkeypatch.setattr(celery_app, "build_kafka_producer", lambda: producer)
    return producer
