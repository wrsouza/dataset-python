"""Shared pytest fixtures for the Price Alerts test suite.

The test environment has no Kafka broker available, so unit and
integration tests rely on KafkaPriceMonitor's documented fallback: when
`kafka-python` is not installed (or the broker is unreachable),
`notify_price_change` automatically falls back to direct in-process
fan-out (`_fan_out`). This lets us validate the full Observer wiring
(subscribe -> notify -> observer) without a running broker.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from price_alerts.infrastructure.kafka_subject import KafkaPriceMonitor


@pytest.fixture
def monitor() -> KafkaPriceMonitor:
    """A KafkaPriceMonitor pointed at a non-existent broker.

    Kafka calls fail fast and the Subject falls back to direct fan-out,
    which is exactly what we want for fast, deterministic unit tests.
    """
    return KafkaPriceMonitor(kafka_bootstrap="unreachable-broker:9092")


@pytest.fixture
def flask_app() -> Iterator[object]:
    """Flask test app with a fresh KafkaPriceMonitor (isolated from main.monitor)."""
    import price_alerts.main as main_module

    original_monitor = main_module.monitor
    main_module.monitor = KafkaPriceMonitor(kafka_bootstrap="unreachable-broker:9092")
    main_module.app = main_module.create_app()
    yield main_module.app
    main_module.monitor = original_monitor


@pytest.fixture
def client(flask_app: object) -> Iterator[object]:
    with flask_app.test_client() as test_client:  # type: ignore[attr-defined]
        yield test_client
