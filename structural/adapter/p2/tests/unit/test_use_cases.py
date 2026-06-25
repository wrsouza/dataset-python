"""Unit tests for user use cases — repository is mocked."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from orm_adapter.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from orm_adapter.domain.entities import User, UserNotFoundError


def _make_user(**kwargs: object) -> User:
    defaults = {"id": 1, "name": "Alice", "email": "alice@test.com", "is_active": True}
    defaults.update(kwargs)
    return User(**defaults)  # type: ignore[arg-type]


class TestGetUser:
    def test_returns_user(self) -> None:
        repo = MagicMock()
        repo.find_by_id.return_value = _make_user()
        result = GetUserUseCase(repository=repo).execute(1)
        assert result.id == 1

    def test_raises_when_none(self) -> None:
        repo = MagicMock()
        repo.find_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            GetUserUseCase(repository=repo).execute(1)


class TestListUsers:
    def test_returns_list(self) -> None:
        repo = MagicMock()
        repo.find_all.return_value = [_make_user(), _make_user(id=2)]
        result = ListUsersUseCase(repository=repo).execute()
        assert len(result) == 2


class TestCreateUser:
    def test_saves_and_returns(self) -> None:
        repo = MagicMock()
        repo.save.return_value = _make_user(id=10)
        result = CreateUserUseCase(repository=repo).execute("Alice", "alice@test.com")
        assert result.id == 10
        saved_arg: User = repo.save.call_args[0][0]
        assert saved_arg.name == "Alice"


class TestDeleteUser:
    def test_calls_delete(self) -> None:
        repo = MagicMock()
        DeleteUserUseCase(repository=repo).execute(1)
        repo.delete.assert_called_once_with(1)


class TestUpdateUser:
    def test_updates_and_returns(self) -> None:
        repo = MagicMock()
        repo.find_by_id.return_value = _make_user(id=1, is_active=False)
        repo.save.return_value = _make_user(id=1, name="New", email="new@test.com")
        result = UpdateUserUseCase(repository=repo).execute(
            user_id=1, name="New", email="new@test.com"
        )
        assert result.name == "New"
        saved_arg: User = repo.save.call_args[0][0]
        assert saved_arg.is_active is False

    def test_raises_when_not_found(self) -> None:
        repo = MagicMock()
        repo.find_by_id.return_value = None
        with pytest.raises(UserNotFoundError):
            UpdateUserUseCase(repository=repo).execute(
                user_id=1, name="New", email="new@test.com"
            )
