"""Integration tests for the Flask Discount Strategy API."""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_apply_percentage_discount(client: FlaskClient) -> None:
    response = client.post(
        "/discounts/apply",
        json={
            "strategy": "percentage",
            "original_total": 100.0,
            "params": {"percentage": 10},
        },
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["discount_amount"] == 10.0
    assert body["final_total"] == 90.0


def test_apply_bulk_quantity_discount_respects_threshold(client: FlaskClient) -> None:
    response = client.post(
        "/discounts/apply",
        json={
            "strategy": "bulk_quantity",
            "original_total": 100.0,
            "quantity": 20,
            "params": {"threshold": 10, "percentage": 15},
        },
    )

    assert response.get_json()["discount_amount"] == 15.0


def test_apply_unknown_strategy_returns_400(client: FlaskClient) -> None:
    response = client.post(
        "/discounts/apply",
        json={"strategy": "unknown", "original_total": 100.0},
    )

    assert response.status_code == 400


def test_get_history_lists_applied_discounts(client: FlaskClient) -> None:
    client.post(
        "/discounts/apply",
        json={"strategy": "no_discount", "original_total": 50.0},
    )

    response = client.get("/discounts/history")

    body = response.get_json()
    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["strategy_name"] == "no_discount"


def test_list_strategies(client: FlaskClient) -> None:
    response = client.get("/discounts/strategies")

    body = response.get_json()
    assert "percentage" in body
    assert "fixed_amount" in body
