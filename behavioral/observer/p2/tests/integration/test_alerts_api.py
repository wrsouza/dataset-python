"""Integration tests for the Flask Price Alerts API.

No Kafka broker is available in this environment. We rely on the same
fallback documented in `tests/conftest.py`: KafkaPriceMonitor automatically
falls back to direct in-process fan-out when the broker is unreachable,
so the full HTTP flow (register -> publish price -> observer notified) can
be exercised end-to-end through the Flask test client without docker-compose.
"""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_alert_returns_subscription(client: FlaskClient) -> None:
    response = client.post(
        "/alerts",
        json={
            "channel": "email",
            "target": "buyer@example.com",
            "product_id": "SKU-1",
            "threshold": 5.0,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert "subscription_id" in body
    assert body["channel"] == "email"
    assert body["product_id"] == "SKU-1"


def test_create_alert_rejects_unsupported_channel(client: FlaskClient) -> None:
    response = client.post(
        "/alerts",
        json={
            "channel": "carrier-pigeon",
            "target": "x",
            "product_id": "SKU-1",
            "threshold": 5.0,
        },
    )

    assert response.status_code == 400


def test_create_alert_rejects_missing_fields(client: FlaskClient) -> None:
    response = client.post("/alerts", json={"channel": "sms"})
    assert response.status_code == 400


def test_list_alerts_returns_registered_subscriptions(client: FlaskClient) -> None:
    client.post(
        "/alerts",
        json={
            "channel": "sms",
            "target": "+15550000",
            "product_id": "SKU-2",
            "threshold": 3.0,
        },
    )

    response = client.get("/alerts")

    assert response.status_code == 200
    body = response.get_json()
    assert any(item["product_id"] == "SKU-2" for item in body)


def test_delete_alert_removes_subscription(client: FlaskClient) -> None:
    create_response = client.post(
        "/alerts",
        json={
            "channel": "webhook",
            "target": "https://example.com/hook",
            "product_id": "SKU-3",
            "threshold": 2.0,
        },
    )
    subscription_id = create_response.get_json()["subscription_id"]

    delete_response = client.delete(f"/alerts/{subscription_id}")
    list_response = client.get("/alerts")

    assert delete_response.status_code == 200
    assert all(
        item["subscription_id"] != subscription_id for item in list_response.get_json()
    )


def test_publish_price_triggers_registered_observer(client: FlaskClient) -> None:
    client.post(
        "/alerts",
        json={
            "channel": "email",
            "target": "watcher@example.com",
            "product_id": "SKU-4",
            "threshold": 5.0,
        },
    )

    response = client.post(
        "/prices/SKU-4",
        json={"old_price": 100.0, "new_price": 120.0},
    )

    assert response.status_code == 202


def test_publish_price_requires_both_prices(client: FlaskClient) -> None:
    response = client.post("/prices/SKU-5", json={"old_price": 100.0})
    assert response.status_code == 400
