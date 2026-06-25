"""Unit tests for RoleAuthorizationHandler in isolation (mocked next handler)."""

from __future__ import annotations

from unittest.mock import MagicMock

from validation.domain.entities import APIRequest, UserRole
from validation.infrastructure.handlers.role_authorization import (
    RoleAuthorizationHandler,
)


def test_handle_rejects_request_without_role() -> None:
    handler = RoleAuthorizationHandler()
    request = APIRequest(body={}, user_role=None, endpoint="/orders")

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 403


def test_handle_rejects_unknown_endpoint() -> None:
    handler = RoleAuthorizationHandler()
    request = APIRequest(body={}, user_role=UserRole.ADMIN, endpoint="/unmapped")

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 403


def test_handle_rejects_insufficient_role_for_admin_endpoint() -> None:
    handler = RoleAuthorizationHandler()
    request = APIRequest(body={}, user_role=UserRole.USER, endpoint="/admin")

    response = handler.handle(request)

    assert response is not None
    assert response.status_code == 403
    assert response.handler_name == "RoleAuthorizationHandler"


def test_handle_passes_sufficient_role_to_next_handler() -> None:
    handler = RoleAuthorizationHandler()
    mock_next = MagicMock(handle=MagicMock(return_value=None))
    handler.set_next(mock_next)
    request = APIRequest(body={}, user_role=UserRole.MANAGER, endpoint="/orders")

    response = handler.handle(request)

    assert response is None
    mock_next.handle.assert_called_once_with(request)


def test_handle_allows_guest_on_public_endpoint() -> None:
    handler = RoleAuthorizationHandler()
    handler.set_next(MagicMock(handle=MagicMock(return_value=None)))
    request = APIRequest(body={}, user_role=UserRole.GUEST, endpoint="/public")

    response = handler.handle(request)

    assert response is None
