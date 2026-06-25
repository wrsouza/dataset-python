"""Application layer — CRUD use cases depending only on UserRepository (Target).

No ORM imports. No SQL. Pure domain logic and the Target interface.
"""

from __future__ import annotations

from orm_adapter.domain.entities import User, UserNotFoundError
from orm_adapter.domain.interfaces import UserRepository


class GetUserUseCase:
    """Retrieve a user or raise UserNotFoundError."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def execute(self, user_id: int) -> User:
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user


class ListUsersUseCase:
    """List all users."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def execute(self) -> list[User]:
        return self._repo.find_all()


class CreateUserUseCase:
    """Persist a new user entity."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def execute(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        return self._repo.save(user)


class UpdateUserUseCase:
    """Update an existing user's details."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def execute(self, user_id: int, name: str, email: str) -> User:
        existing = self._repo.find_by_id(user_id)
        if existing is None:
            raise UserNotFoundError(user_id)
        updated = User(id=user_id, name=name, email=email, is_active=existing.is_active)
        return self._repo.save(updated)


class DeleteUserUseCase:
    """Remove a user by ID."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    def execute(self, user_id: int) -> None:
        self._repo.delete(user_id)
