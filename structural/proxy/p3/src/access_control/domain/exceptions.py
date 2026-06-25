"""Domain exceptions for the access_control package."""

from __future__ import annotations


class DocumentNotFoundError(Exception):
    """Raised when a requested document does not exist."""

    def __init__(self, doc_id: str) -> None:
        self.doc_id = doc_id
        super().__init__(f"Document not found: {doc_id!r}")


class PermissionDeniedError(Exception):
    """Raised when the current user lacks permission for an action."""

    def __init__(self, user_id: str, action: str, doc_id: str) -> None:
        self.user_id = user_id
        self.action = action
        self.doc_id = doc_id
        super().__init__(
            f"User {user_id!r} is not allowed to {action!r} document {doc_id!r}"
        )


class InactiveUserError(Exception):
    """Raised when an inactive user attempts any operation."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id!r} account is inactive")
