"""Target interface — UserRepository Protocol.

ISP: four focused methods; no extra surface area.
DIP: use cases depend on this, not on SQLAlchemy or pymysql.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from orm_adapter.domain.entities import User


@runtime_checkable
class UserRepository(Protocol):
    """Target: unified repository interface for user persistence.

    Both ORM adapters (SQLAlchemy and raw MySQL) implement this
    protocol structurally — no inheritance required.
    """

    def find_by_id(self, user_id: int) -> User | None:
        """Return the user with the given ID, or None if not found."""
        ...

    def find_all(self) -> list[User]:
        """Return all users in the store."""
        ...

    def save(self, user: User) -> User:
        """Persist a user (insert or update). Returns the persisted User with id."""
        ...

    def delete(self, user_id: int) -> None:
        """Remove a user by ID. Raises UserNotFoundError if absent."""
        ...
