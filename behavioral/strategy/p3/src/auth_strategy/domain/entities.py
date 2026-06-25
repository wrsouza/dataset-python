"""Domain entities for the Authentication Strategy system."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthResult:
    """Immutable outcome of an authentication attempt."""

    success: bool
    strategy_name: str
    user_id: str | None = None
    reason: str | None = None
