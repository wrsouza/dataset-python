"""Domain interfaces for the Game Particle System — Flyweight pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from particle_system.domain.entities import Particle, ParticleType


class ParticleTypeFactoryABC(ABC):
    """FlyweightFactory: creates and caches ParticleType objects by name.

    OCP: new particle kinds are added by registering them through
    `register_type`, never by editing the factory's internals or by adding
    `if/elif` branches for each kind.
    """

    @abstractmethod
    def get_or_create(self, name: str) -> ParticleType:
        """Return the cached flyweight for `name`, building it on first use."""
        ...

    @abstractmethod
    def register_type(self, particle_type: ParticleType) -> None:
        """Register a new particle kind so future lookups can resolve it."""
        ...

    @abstractmethod
    def get_flyweight_count(self) -> int:
        """Return the number of unique flyweights currently cached."""
        ...

    @abstractmethod
    def get_cached_names(self) -> tuple[str, ...]:
        """Return the names of all flyweights currently cached, in insertion order."""
        ...


class PhysicsProtocol(Protocol):
    """Abstraction for particle motion — DIP boundary between simulation and physics.

    The application layer depends only on this Protocol, never on a concrete
    physics implementation, so the simulation can swap gravity, drag, or any
    other motion model without changing a single line of use-case code.
    """

    def step(self, particle: Particle, delta_seconds: float) -> None:
        """Advance `particle`'s extrinsic state in place by `delta_seconds`."""
        ...
