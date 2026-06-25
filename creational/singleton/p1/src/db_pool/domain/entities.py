"""Domain entities for the Database Connection Pool project."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class User:
    """Immutable user entity.

    frozen=True enforces value-object semantics — IDs and emails do not change
    after creation, preventing accidental mutation in application code.
    """

    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class PoolStatsSnapshot:
    """Concrete value object for pool statistics.

    Mutable because stats are sampled at a point in time and not reused.
    """

    size: int
    free: int
    used: int
    min_size: int
    max_size: int
    sampled_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "size": self.size,
            "free": self.free,
            "used": self.used,
            "min_size": self.min_size,
            "max_size": self.max_size,
            "sampled_at": self.sampled_at.isoformat(),
        }


@dataclass(frozen=True)
class CreateUserRequest:
    """Input DTO for the create-user use case.

    Using a dataclass instead of raw dicts makes the contract explicit and
    enables static type checking across boundaries.
    """

    name: str
    email: str
