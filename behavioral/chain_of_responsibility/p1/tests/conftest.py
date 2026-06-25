"""Shared pytest fixtures for the request validation chain tests."""

from __future__ import annotations

import base64
import json
from collections.abc import Callable

import pytest

from validation.domain.entities import APIRequest, UserRole
from validation.infrastructure.handlers.rate_limit import _SlidingWindowCounter


def _encode_fake_jwt(sub: str, role: str) -> str:
    """Build a base64 'JWT' compatible with JWTAuthHandler's fake decoder."""
    header = base64.urlsafe_b64encode(b'{"alg":"none"}').decode().rstrip("=")
    payload_bytes = json.dumps({"sub": sub, "role": role}).encode()
    payload = base64.urlsafe_b64encode(payload_bytes).decode().rstrip("=")
    signature = "fakesignature"
    return f"{header}.{payload}.{signature}"


@pytest.fixture
def make_jwt() -> Callable[[str, str], str]:
    """Factory fixture returning a fake JWT string for a given user/role."""
    return _encode_fake_jwt


@pytest.fixture
def valid_order_body() -> dict[str, object]:
    """A request body that satisfies OrderSchema."""
    return {
        "product_id": "prod-123",
        "quantity": 2,
        "price": 19.90,
        "customer_id": "cust-456",
    }


@pytest.fixture
def auth_headers(make_jwt: Callable[[str, str], str]) -> dict[str, str]:
    """Authorization header carrying a valid USER-role fake JWT."""
    token = make_jwt("user-1", UserRole.USER.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_api_request(
    valid_order_body: dict[str, object],
    auth_headers: dict[str, str],
) -> APIRequest:
    """A fully valid APIRequest ready to pass the entire chain."""
    return APIRequest(
        body=valid_order_body,
        headers=auth_headers,
        client_ip="10.0.0.1",
        endpoint="/orders",
    )


@pytest.fixture(autouse=True)
def _reset_rate_limit_state() -> None:
    """Ensure the module-level rate limit counter doesn't leak between tests."""
    from validation.infrastructure.handlers import rate_limit as rate_limit_module

    rate_limit_module._default_counter = _SlidingWindowCounter(
        limit=10, window_seconds=60.0
    )
