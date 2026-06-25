"""Application use cases for the Database Connection Pool project.

Each use case has a single responsibility and depends only on domain
abstractions, never on infrastructure details (DIP).
"""

from __future__ import annotations

from typing import Any

from db_pool.domain.entities import CreateUserRequest, PoolStatsSnapshot
from db_pool.domain.interfaces import ConnectionPool, UserRepository


class GetPoolStatsUseCase:
    """Retrieve current pool statistics.

    SRP: only responsibility is to delegate the stats query.
    """

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    async def execute(self) -> PoolStatsSnapshot:
        return await self._pool.get_stats()  # type: ignore[return-value]


class ListUsersUseCase:
    """Return all users from persistence.

    Depends on UserRepository abstraction — works with Postgres, SQLite,
    or an in-memory fake without modification (OCP).
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[dict[str, Any]]:
        return await self._repository.find_all()


class CreateUserUseCase:
    """Create and persist a new user.

    Validates the request DTO before delegating to the repository.
    Business rule: email must contain '@' (simplistic but illustrative).
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, request: CreateUserRequest) -> dict[str, Any]:
        self._validate(request)
        return await self._repository.create(name=request.name, email=request.email)

    @staticmethod
    def _validate(request: CreateUserRequest) -> None:
        if not request.name.strip():
            raise ValueError("name must not be blank")
        if "@" not in request.email:
            raise ValueError(f"'{request.email}' is not a valid email address")


class GetUserByIdUseCase:
    """Fetch a single user by primary key."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: int) -> dict[str, Any] | None:
        return await self._repository.find_by_id(user_id)
