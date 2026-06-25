"""Concrete in-memory FlyweightFactory for ParticleType."""

from __future__ import annotations

from particle_system.domain.entities import ParticleType
from particle_system.domain.interfaces import ParticleTypeFactoryABC

# Built-in particle kinds — intrinsic state per kind. New kinds can be added
# here or registered at runtime via `register_type`, without touching the
# factory's lookup logic (Open/Closed Principle).
_DEFAULT_PARTICLE_TYPES: dict[str, ParticleType] = {
    "fire": ParticleType(
        name="fire",
        sprite="sprites/fire.png",
        color="#FF4500",
        base_lifetime_seconds=1.2,
        drag_coefficient=0.05,
    ),
    "spark": ParticleType(
        name="spark",
        sprite="sprites/spark.png",
        color="#FFD700",
        base_lifetime_seconds=0.6,
        drag_coefficient=0.02,
    ),
    "smoke": ParticleType(
        name="smoke",
        sprite="sprites/smoke.png",
        color="#888888",
        base_lifetime_seconds=2.5,
        drag_coefficient=0.15,
    ),
}

# Estimated bytes occupied by a ParticleType's intrinsic data (sprite path,
# color string, floats, object overhead) when it lives as ONE shared object.
_FLYWEIGHT_INTRINSIC_SIZE_BYTES = 256
# Estimated bytes the same intrinsic data would cost if duplicated inside
# every single particle instead of being shared via the Flyweight.
_INTRINSIC_PER_PARTICLE_BYTES = 256
# Estimated bytes for the extrinsic state (x, y, vx, vy, age) plus a
# reference to the shared flyweight — this cost is paid regardless of Flyweight use.
_EXTRINSIC_PER_PARTICLE_BYTES = 96


class ParticleTypeFactory(ParticleTypeFactoryABC):
    """FlyweightFactory that caches ParticleType instances by name.

    A single dict acts as the cache: the first request for a given name
    builds the ParticleType once; every subsequent request for that same
    name returns the exact same object (`is` identity), which is the core
    Flyweight guarantee.
    """

    def __init__(self) -> None:
        self._cache: dict[str, ParticleType] = dict(_DEFAULT_PARTICLE_TYPES)

    def get_or_create(self, name: str) -> ParticleType:
        """Return the shared Flyweight for `name`, creating a fallback if unknown."""
        if name in self._cache:
            return self._cache[name]

        fallback = ParticleType(
            name=name,
            sprite="sprites/unknown.png",
            color="#FFFFFF",
            base_lifetime_seconds=1.0,
            drag_coefficient=0.05,
        )
        self._cache[name] = fallback
        return fallback

    def register_type(self, particle_type: ParticleType) -> None:
        """Register a new particle kind, making it available to future lookups.

        This is the OCP extension point: callers add new kinds (e.g.
        "magic_spark") without modifying this class's source code.
        """
        self._cache[particle_type.name] = particle_type

    def get_flyweight_count(self) -> int:
        """Return the number of unique ParticleType flyweights cached."""
        return len(self._cache)

    def get_cached_names(self) -> tuple[str, ...]:
        """Return the names of all cached flyweights, in insertion order."""
        return tuple(self._cache.keys())

    def estimate_bytes_without_flyweight(self, total_particles: int) -> int:
        """Estimate memory if every particle duplicated its own intrinsic data."""
        return total_particles * (
            _INTRINSIC_PER_PARTICLE_BYTES + _EXTRINSIC_PER_PARTICLE_BYTES
        )

    def estimate_bytes_with_flyweight(self, total_particles: int) -> int:
        """Estimate memory with intrinsic data shared via the Flyweight cache."""
        shared_intrinsic = self.get_flyweight_count() * _FLYWEIGHT_INTRINSIC_SIZE_BYTES
        per_particle = total_particles * _EXTRINSIC_PER_PARTICLE_BYTES
        return shared_intrinsic + per_particle
