"""Domain interfaces for the Auth Provider Factory pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class AuthProvider(Protocol):
    """Product interface — all auth providers must implement this contract.

    LSP is enforced here: every concrete provider returns the same types
    and raises only domain exceptions (not framework-specific ones).
    """

    def authenticate(self, credentials: dict[str, Any]) -> str:
        """Authenticate with the given credentials and return a user identifier.

        Args:
            credentials: Dict with keys like 'username'/'password' or 'token'.

        Returns:
            User identifier string (username, email, or user ID).

        Raises:
            AuthenticationError: if credentials are invalid.
        """
        ...

    def issue_token(self, user_id: str) -> str:
        """Issue an opaque token for the authenticated user.

        Args:
            user_id: Identifier of the authenticated user.

        Returns:
            An opaque token string the client can present on future requests.
        """
        ...

    def validate_token(self, token: str) -> str:
        """Validate a token and return the associated user identifier.

        Args:
            token: The token previously issued by issue_token().

        Returns:
            User identifier if valid.

        Raises:
            InvalidTokenError: if the token is expired or tampered.
        """
        ...

    def revoke(self, token: str) -> None:
        """Invalidate the given token so it cannot be used again.

        Args:
            token: The token to revoke.
        """
        ...


class AuthProviderFactory(ABC):
    """Creator — subclasses decide which AuthProvider to create.

    The middleware and views depend on this abstract class (DIP).
    New auth schemes are added without changing existing code (OCP).
    """

    @abstractmethod
    def create_provider(self) -> AuthProvider:
        """Factory method: returns the AuthProvider for this scheme."""
        ...

    def get_scheme_name(self) -> str:
        """Return the name of this auth scheme."""
        return self.__class__.__name__.replace("AuthFactory", "")
