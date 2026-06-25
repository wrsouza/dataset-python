"""Abstractions for the Prototype pattern and profile persistence.

Kept dependency-free (no Typer, no JSON, no filesystem) so the domain layer
can be unit tested and reused regardless of how profiles are stored or
exposed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.infra_profile.domain.entities import InfrastructureProfile


class Prototype(ABC):
    """Contract for any object that knows how to clone itself.

    This is the Prototype pattern's core interface: instead of a factory or
    constructor rebuilding an object field by field, the object itself
    produces an independent copy of its current state.
    """

    @abstractmethod
    def clone(self) -> Prototype:
        """Return a fully independent copy of this object."""


class ProfileRepository(Protocol):
    """Persistence contract for infrastructure profiles.

    The application layer depends on this Protocol, never on a concrete
    storage technology (Dependency Inversion). Swapping the JSON file
    adapter for a database or cloud-API adapter requires no changes to the
    use cases, only a new class implementing this contract.
    """

    def save(self, profile: InfrastructureProfile) -> None:
        """Persist a profile, overwriting any existing one with the same name."""
        ...

    def get(self, name: str) -> InfrastructureProfile | None:
        """Return the stored profile with the given name, or None."""
        ...

    def list_all(self) -> list[InfrastructureProfile]:
        """Return every profile currently persisted."""
        ...
