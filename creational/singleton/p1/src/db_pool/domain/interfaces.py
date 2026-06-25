"""Domain interfaces for the Database Connection Pool.

Defines abstractions that decouple high-level modules from
concrete infrastructure implementations (DIP).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class ConnectionPool(Protocol):
    """Contract for any connection pool implementation.

    Clients depend on this abstraction, not on asyncpg or SQLAlchemy directly.
    Satisfies DIP: high-level modules (endpoints) depend on abstractions.
    """

    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        ...

    async def release(self, connection: Any) -> None:
        """Return a connection to the pool."""
        ...

    async def get_stats(self) -> PoolStats:
        """Return current pool statistics."""
        ...

    async def close(self) -> None:
        """Gracefully shut down the pool."""
        ...


class UserRepository(Protocol):
    """Contract for user data access.

    SRP: only responsible for user persistence, nothing else.
    """

    async def find_all(self) -> list[dict[str, Any]]:
        """Return all users."""
        ...

    async def create(self, name: str, email: str) -> dict[str, Any]:
        """Persist a new user and return the created record."""
        ...

    async def find_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Return a single user or None if not found."""
        ...


class PoolStats(ABC):
    """Value object representing pool statistics at a point in time."""

    @property
    @abstractmethod
    def size(self) -> int:
        """Total connections in the pool."""
        ...

    @property
    @abstractmethod
    def free(self) -> int:
        """Available (idle) connections."""
        ...

    @property
    @abstractmethod
    def used(self) -> int:
        """Connections currently checked out."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dictionary for API responses."""
        ...
