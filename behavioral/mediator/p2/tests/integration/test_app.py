"""Integration tests for the Flask event bus API."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from event_bus.app import create_app
from event_bus.infrastructure.rabbitmq_event_bus import RabbitMQEventBus
from tests.unit.test_rabbitmq_event_bus import FakeChannel


@pytest.fixture
def client() -> FlaskClient:
    app = create_app(bus=RabbitMQEventBus(FakeChannel()))
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_publish_event_returns_201(client: FlaskClient) -> None:
    response = client.post(
        "/events", json={"event_type": "order.created", "payload": {"order_id": "o-1"}}
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["event_type"] == "order.created"


def test_published_event_appears_in_log(client: FlaskClient) -> None:
    client.post("/events", json={"event_type": "order.created", "payload": {}})
    client.post("/events", json={"event_type": "order.cancelled", "payload": {}})

    response = client.get("/events/log")

    event_types = [e["event_type"] for e in response.get_json()]
    assert event_types == ["order.created", "order.cancelled"]
