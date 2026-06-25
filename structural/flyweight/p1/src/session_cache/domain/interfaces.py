"""Domain interfaces for Session Token Cache — Flyweight pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol


class SessionMetadataProtocol(Protocol):
    """Flyweight: immutable intrinsic state shared across sessions of the same role."""

    @property
    def role(self) -> str: ...

    @property
    def permissions(self) -> frozenset[str]: ...

    @property
    def app_version(self) -> str: ...

    @property
    def max_session_duration(self) -> int: ...


class SessionMetadataFactoryABC(ABC):
    """FlyweightFactory: creates and caches SessionMetadata objects by role."""

    @abstractmethod
    def get_or_create(self, role: str) -> SessionMetadataProtocol:
        """Return cached flyweight for role, or create and cache a new one."""
        ...

    @abstractmethod
    def get_flyweight_count(self) -> int:
        """Return number of unique flyweights currently cached."""
        ...

    @abstractmethod
    def get_cache_stats(self) -> dict[str, int | float]:
        """Return memory economy statistics."""
        ...


class SessionRepositoryProtocol(Protocol):
    """Repository for UserSession persistence."""

    def save(self, token: str, session_data: dict[str, object]) -> None: ...

    def find(self, token: str) -> dict[str, object] | None: ...

    def delete(self, token: str) -> None: ...

    def count_active(self) -> int: ...
