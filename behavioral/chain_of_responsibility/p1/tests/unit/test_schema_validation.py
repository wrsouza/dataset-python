"""Unit tests for SchemaValidationHandler in isolation (mocked next handler)."""

from __future__ import annotations

from unittest.mock import MagicMock

from validation.domain.entities import APIRequest
from validation.infrastructure.handlers.schema_validation import (
    SchemaValidationHandler,
)


def test_handle_passes_valid_body_to_next_handler(
    valid_order_body: dict[str, object],
) -> None:
    handler = SchemaValidationHandler()
    mock_next = MagicMock(handle=MagicMock(return_value=None))
    handler.set_next(mock_next)
    request = APIRequest(body=valid_order_body)

    response = handler.handle(request)

    assert response is None
    mock_next.handle.assert_called_once_with(request)


def test_handle_rejects_missing_required_field() -> None:
    handler = SchemaValidationHandler()
    request = APIRequest(body={"product_id": "p1", "quantity": 1, "price": 10.0})

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 422
    assert response.handler_name == "SchemaValidationHandler"


def test_handle_rejects_non_positive_quantity(
    valid_order_body: dict[str, object],
) -> None:
    handler = SchemaValidationHandler()
    body = {**valid_order_body, "quantity": 0}
    request = APIRequest(body=body)

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 422


def test_handle_rejects_non_positive_price(
    valid_order_body: dict[str, object],
) -> None:
    handler = SchemaValidationHandler()
    body = {**valid_order_body, "price": -1.0}
    request = APIRequest(body=body)

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 422


def test_handle_rejects_blank_customer_id(
    valid_order_body: dict[str, object],
) -> None:
    handler = SchemaValidationHandler()
    body = {**valid_order_body, "customer_id": "   "}
    request = APIRequest(body=body)

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 422
