"""Integration tests for the Flask Shopping Cart Visitors API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_price_operation(client: FlaskClient) -> None:
    response = client.post(
        "/carts/operations/price",
        json={
            "items": [
                {
                    "type": "physical",
                    "name": "Book",
                    "unit_price": 10.0,
                    "quantity": 1,
                    "weight_kg": 0.5,
                },
                {
                    "type": "digital",
                    "name": "E-book",
                    "unit_price": 5.0,
                    "quantity": 1,
                },
            ]
        },
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["data"]["subtotal"] == 15.0


def test_shipping_operation(client: FlaskClient) -> None:
    response = client.post(
        "/carts/operations/shipping",
        json={
            "items": [
                {
                    "type": "physical",
                    "name": "Book",
                    "unit_price": 10.0,
                    "quantity": 2,
                    "weight_kg": 1.0,
                }
            ]
        },
    )

    body = response.get_json()
    assert body["data"]["total_weight_kg"] == 2.0


def test_invoice_operation(client: FlaskClient) -> None:
    response = client.post(
        "/carts/operations/invoice",
        json={
            "items": [
                {
                    "type": "subscription",
                    "name": "Pro Plan",
                    "unit_price": 10.0,
                    "quantity": 1,
                    "billing_period": "monthly",
                }
            ]
        },
    )

    body = response.get_json()
    assert "Pro Plan" in body["data"]["lines"][0]


def test_unknown_operation_returns_400(client: FlaskClient) -> None:
    response = client.post("/carts/operations/unknown", json={"items": []})

    assert response.status_code == 400


def test_unknown_item_type_returns_400(client: FlaskClient) -> None:
    response = client.post(
        "/carts/operations/price", json={"items": [{"type": "unknown"}]}
    )

    assert response.status_code == 400


def test_get_history_after_operation(client: FlaskClient) -> None:
    client.post(
        "/carts/operations/price",
        json={
            "items": [
                {
                    "type": "digital",
                    "name": "E-book",
                    "unit_price": 5.0,
                    "quantity": 1,
                }
            ]
        },
    )

    response = client.get("/carts/operations/price/history")

    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 1


def test_get_history_unknown_operation_returns_400(client: FlaskClient) -> None:
    response = client.get("/carts/operations/unknown/history")

    assert response.status_code == 400
