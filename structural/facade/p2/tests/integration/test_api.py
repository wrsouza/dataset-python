"""Integration tests — full HTTP -> PaymentFacade -> subsystems flow.

The Flask app is exercised through its test client. Stripe is replaced by
MockStripeGateway (USE_MOCK_STRIPE=true) and MySQL by SQLite, but the route
handlers, the Facade and the SQL repository all run exactly as in production.
"""

from __future__ import annotations

from flask.testing import FlaskClient

VALID_VISA_NUMBER = "4242424242424242"
DECLINED_VISA_NUMBER = "4000000000000002"


def _payment_payload(card_number: str = VALID_VISA_NUMBER) -> dict[str, object]:
    return {
        "customer_id": "cus_1",
        "customer_name": "Ada Lovelace",
        "customer_email": "ada@example.com",
        "card_number": card_number,
        "card_exp_month": 12,
        "card_exp_year": 2099,
        "card_cvc": "123",
        "amount_cents": 2500,
        "currency": "usd",
    }


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_charge_payment_success(client: FlaskClient) -> None:
    response = client.post("/payments", json=_payment_payload())

    assert response.status_code == 201
    body = response.get_json()
    assert body["status"] == "approved"
    assert body["amount_cents"] == 2500
    assert body["receipt_id"].startswith("rcpt_")


def test_charge_payment_with_invalid_card_returns_400(client: FlaskClient) -> None:
    payload = _payment_payload(card_number="not-a-card")
    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_charge_payment_declined_returns_402(client: FlaskClient) -> None:
    response = client.post("/payments", json=_payment_payload(DECLINED_VISA_NUMBER))

    assert response.status_code == 402
    body = response.get_json()
    assert "transaction_id" in body


def test_get_payment_after_charge(client: FlaskClient) -> None:
    create_response = client.post("/payments", json=_payment_payload())
    transaction_id = create_response.get_json()["transaction_id"]

    response = client.get(f"/payments/{transaction_id}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["transaction_id"] == transaction_id
    assert body["status"] == "approved"


def test_get_payment_not_found_returns_404(client: FlaskClient) -> None:
    response = client.get("/payments/does-not-exist")
    assert response.status_code == 404


def test_refund_payment_success(client: FlaskClient) -> None:
    create_response = client.post("/payments", json=_payment_payload())
    transaction_id = create_response.get_json()["transaction_id"]

    response = client.post(f"/payments/{transaction_id}/refund")

    assert response.status_code == 200
    assert response.get_json()["status"] == "refunded"


def test_refund_payment_not_found_returns_404(client: FlaskClient) -> None:
    response = client.post("/payments/does-not-exist/refund")
    assert response.status_code == 404


def test_refund_payment_twice_returns_409(client: FlaskClient) -> None:
    create_response = client.post("/payments", json=_payment_payload())
    transaction_id = create_response.get_json()["transaction_id"]
    client.post(f"/payments/{transaction_id}/refund")

    second_response = client.post(f"/payments/{transaction_id}/refund")

    assert second_response.status_code == 409
