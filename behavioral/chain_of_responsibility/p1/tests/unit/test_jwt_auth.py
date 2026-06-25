"""Unit tests for JWTAuthHandler in isolation (mocked next handler)."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import MagicMock

from validation.domain.entities import APIRequest, APIResponse, UserRole
from validation.infrastructure.handlers.jwt_auth import JWTAuthHandler


def test_handle_rejects_missing_authorization_header() -> None:
    handler = JWTAuthHandler()
    request = APIRequest(body={}, headers={})

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 401
    assert response.handler_name == "JWTAuthHandler"


def test_handle_rejects_malformed_bearer_token() -> None:
    handler = JWTAuthHandler()
    request = APIRequest(body={}, headers={"Authorization": "Bearer not.a.validjwt$$"})

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 401


def test_handle_passes_valid_token_to_next_handler(
    make_jwt: Callable[[str, str], str],
) -> None:
    handler = JWTAuthHandler()
    mock_next = MagicMock()
    mock_next.handle.return_value = None
    handler.set_next(mock_next)

    token = make_jwt("user-42", UserRole.ADMIN.value)
    request = APIRequest(body={}, headers={"Authorization": f"Bearer {token}"})

    handler.handle(request)

    mock_next.handle.assert_called_once_with(request)
    assert request.user_id == "user-42"
    assert request.user_role == UserRole.ADMIN


def test_handle_defaults_to_guest_role_for_unknown_role(
    make_jwt: Callable[[str, str], str],
) -> None:
    handler = JWTAuthHandler()
    handler.set_next(MagicMock(handle=MagicMock(return_value=None)))

    token = make_jwt("user-7", "superuser")
    request = APIRequest(body={}, headers={"Authorization": f"Bearer {token}"})

    handler.handle(request)

    assert request.user_role == UserRole.GUEST


def test_handle_returns_none_when_no_next_handler_and_token_valid(
    make_jwt: Callable[[str, str], str],
) -> None:
    handler = JWTAuthHandler()
    token = make_jwt("user-1", UserRole.USER.value)
    request = APIRequest(body={}, headers={"Authorization": f"Bearer {token}"})

    response = handler.handle(request)

    assert response is None


def test_handle_result_type_is_api_response_when_rejected() -> None:
    handler = JWTAuthHandler()
    request = APIRequest(body={}, headers={})

    response = handler.handle(request)

    assert isinstance(response, APIResponse)
