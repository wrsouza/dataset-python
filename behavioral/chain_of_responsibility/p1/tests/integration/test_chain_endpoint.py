"""Integration tests for the full validation chain via the FastAPI app."""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from main import app
from validation.domain.entities import UserRole

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_order_succeeds_with_valid_request(
    valid_order_body: dict[str, object],
    auth_headers: dict[str, str],
) -> None:
    response = client.post("/orders", json=valid_order_body, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Request passed all validation handlers"


def test_create_order_fails_without_authorization_header(
    valid_order_body: dict[str, object],
) -> None:
    response = client.post("/orders", json=valid_order_body)

    assert response.status_code == 401
    assert response.json()["handler"] == "JWTAuthHandler"


def test_create_order_fails_when_role_is_unauthorized(
    valid_order_body: dict[str, object],
    make_jwt: Callable[[str, str], str],
) -> None:
    token = make_jwt("guest-1", UserRole.GUEST.value)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/orders", json=valid_order_body, headers=headers)

    assert response.status_code == 403
    assert response.json()["handler"] == "RoleAuthorizationHandler"


def test_create_order_fails_with_invalid_schema(
    auth_headers: dict[str, str],
) -> None:
    invalid_body = {"product_id": "", "quantity": -1, "price": 10.0}

    response = client.post("/orders", json=invalid_body, headers=auth_headers)

    assert response.status_code == 422
    assert response.json()["handler"] == "SchemaValidationHandler"


def test_create_order_short_circuits_at_first_failing_handler_not_last(
    make_jwt: Callable[[str, str], str],
) -> None:
    """An invalid token should fail at JWTAuthHandler, never reaching schema
    validation — proving the chain stops at the first responsible handler."""
    invalid_body = {"product_id": "", "quantity": -1, "price": -10.0}
    headers = {"Authorization": "Bearer garbage"}

    response = client.post("/orders", json=invalid_body, headers=headers)

    assert response.status_code == 401
    assert response.json()["handler"] == "JWTAuthHandler"
