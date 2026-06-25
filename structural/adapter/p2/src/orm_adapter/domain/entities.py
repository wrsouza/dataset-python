"""Domain entities — pure data, no ORM dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class User:
    """Core user entity."""

    name: str
    email: str
    is_active: bool = True
    id: int = field(default=0)


class UserNotFoundError(Exception):
    """Raised when a user cannot be located."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: id={user_id}")


class DuplicateEmailError(Exception):
    """Raised when saving a user with an already-taken email."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email already in use: {email}")
