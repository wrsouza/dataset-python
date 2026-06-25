"""Strategy ABC for the Authentication Strategy system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from auth_strategy.domain.entities import AuthResult


class AuthenticationStrategy(ABC):
    """Abstract base for all authentication strategies.

    OCP: add a new auth mechanism = new subclass, no existing code changes.
    LSP: all subclasses return AuthResult and honor the same contract.
    """

    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> AuthResult:
        """Validate the given credentials and return the outcome."""
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the canonical name of this strategy."""
        ...
