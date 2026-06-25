"""Kafka-backed publisher for ETL completion events."""

from __future__ import annotations

import json
from typing import Protocol


class KafkaProducerLike(Protocol):
    """Minimal kafka-python KafkaProducer contract this publisher relies on."""

    def send(self, topic: str, value: bytes) -> object: ...

    def flush(self) -> None: ...


class KafkaEtlEventPublisher:
    """Publishes a small JSON event every time an ETL pipeline finishes."""

    def __init__(self, producer: KafkaProducerLike, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    def publish_completion(self, pipeline_name: str, records_loaded: int) -> None:
        body = json.dumps(
            {"pipeline_name": pipeline_name, "records_loaded": records_loaded}
        ).encode("utf-8")
        self._producer.send(self._topic, value=body)
        self._producer.flush()
