"""Domain-specific exceptions for the lazy loading proxy project."""

from __future__ import annotations


class UserNotFoundError(Exception):
    """Raised when a user does not exist in the database."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


class AvatarNotFoundError(Exception):
    """Raised when a user has no avatar stored."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"Avatar for user {user_id} not found")


class DatabaseError(Exception):
    """Raised when a database operation fails unexpectedly."""
