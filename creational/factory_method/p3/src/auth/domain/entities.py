"""Domain entities for the auth domain."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthToken:
    """Value object representing an issued auth token."""

    value: str
    scheme: str
    user_id: str
    issued_at: datetime
    expires_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class AuthResult:
    """Value object returned after a successful authentication."""

    user_id: str
    scheme: str
    token: str


class AuthenticationError(Exception):
    """Raised when credentials are invalid."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Authentication failed: {reason}")


class InvalidTokenError(Exception):
    """Raised when a token is expired, revoked, or malformed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Invalid token: {reason}")


class UnsupportedSchemeError(Exception):
    """Raised when an unknown auth scheme is requested."""

    def __init__(self, scheme: str) -> None:
        self.scheme = scheme
        super().__init__(f"Unsupported auth scheme: {scheme}")
