"""Integration tests exercising the FastAPI app end-to-end via TestClient.

Decision: these tests run against a SQLite in-memory database and a
moto-mocked AWS SQS queue (see the `client` fixture in `tests/conftest.py`)
instead of real PostgreSQL/AWS, so the suite is self-contained and does not
require `docker-compose up` to be running. The repository/service classes
under test only use portable SQL and the standard boto3 SQS API, so the
behavior verified here matches production.
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _valid_order_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "customer_id": "CUST001",
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "customer_address": "123 Main St",
        "items": [
            {
                "product_id": "PROD001",
                "quantity": 2,
                "unit_price": 29.99,
                "product_name": "Widget Pro",
            }
        ],
        "card_token": "tok_test_123",
        "card_last_four": "4242",
        "card_brand": "Visa",
    }
    payload.update(overrides)
    return payload


class TestHealthCheck:
    def test_health_check_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPlaceOrder:
    def test_place_order_returns_confirmation(self, client: TestClient) -> None:
        response = client.post("/orders", json=_valid_order_payload())

        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "confirmed"
        assert body["total_amount"] == 59.98
        assert body["tracking_number"]
        assert body["carrier"] == "FastShip"
        assert "order_id" in body

    def test_place_order_reserves_stock(self, client: TestClient) -> None:
        first = client.post("/orders", json=_valid_order_payload())
        assert first.status_code == 201

        depleting_payload = _valid_order_payload(
            items=[
                {
                    "product_id": "PROD003",
                    "quantity": 25,
                    "unit_price": 199.99,
                    "product_name": "Super Gizmo",
                }
            ]
        )
        second = client.post("/orders", json=depleting_payload)
        assert second.status_code == 201

        third = client.post("/orders", json=depleting_payload)
        assert third.status_code == 409

    def test_place_order_with_insufficient_stock_returns_409(
        self, client: TestClient
    ) -> None:
        payload = _valid_order_payload(
            items=[
                {
                    "product_id": "PROD002",
                    "quantity": 9_999,
                    "unit_price": 9.99,
                    "product_name": "Gadget Max",
                }
            ]
        )

        response = client.post("/orders", json=payload)

        assert response.status_code == 409

    def test_place_order_with_declined_card_returns_402(
        self, client: TestClient
    ) -> None:
        payload = _valid_order_payload(card_last_four="0000")

        response = client.post("/orders", json=payload)

        assert response.status_code == 402

    def test_place_order_with_free_shipping_threshold(self, client: TestClient) -> None:
        payload = _valid_order_payload(
            items=[
                {
                    "product_id": "PROD001",
                    "quantity": 4,
                    "unit_price": 29.99,
                    "product_name": "Widget Pro",
                }
            ]
        )

        response = client.post("/orders", json=payload)

        assert response.status_code == 201
        assert response.json()["total_amount"] == 119.96


class TestGetOrder:
    def test_get_order_after_placement_returns_details(
        self, client: TestClient
    ) -> None:
        place_response = client.post("/orders", json=_valid_order_payload())
        order_id = place_response.json()["order_id"]

        response = client.get(f"/orders/{order_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["order_id"] == order_id
        assert body["customer_id"] == "CUST001"
        assert body["status"] == "confirmed"
        assert body["payment_charge_id"] is not None
        assert body["tracking_number"] is not None

    def test_get_unknown_order_returns_404(self, client: TestClient) -> None:
        response = client.get("/orders/does-not-exist")

        assert response.status_code == 404
