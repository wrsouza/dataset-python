"""Domain entities for the Game Particle System — Flyweight pattern.

ParticleType is the Flyweight: a frozen dataclass holding only intrinsic
state (sprite, color, particle kind) that is shared across thousands of
Particle instances. Particle is the Context: it holds extrinsic state
(position, velocity, age) plus a reference to its shared ParticleType.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParticleType:
    """Flyweight — intrinsic state shared by every particle of this kind.

    frozen=True enforces immutability at runtime, which is what makes it
    safe to share a single instance across thousands of `Particle` contexts
    without risk of one particle's behavior corrupting another's.
    """

    name: str
    sprite: str
    color: str
    base_lifetime_seconds: float
    drag_coefficient: float

    def __repr__(self) -> str:
        return (
            f"ParticleType(name={self.name!r}, sprite={self.sprite!r}, "
            f"color={self.color!r})"
        )


@dataclass
class Particle:
    """Context — per-particle (extrinsic) state plus a shared Flyweight reference.

    The ParticleType is NOT duplicated per particle; it is a shared
    reference. Only position, velocity, and age vary per particle.
    """

    x: float
    y: float
    vx: float
    vy: float
    age_seconds: float
    particle_type: ParticleType  # shared Flyweight — same object across particles

    @property
    def type_name(self) -> str:
        """Delegate the kind of particle to the shared Flyweight."""
        return self.particle_type.name

    def is_alive(self) -> bool:
        """Check liveness using extrinsic age against the Flyweight's lifetime."""
        return self.age_seconds < self.particle_type.base_lifetime_seconds

    def to_dict(self) -> dict[str, object]:
        """Serialize this particle for export — only extrinsic state + type key."""
        return {
            "x": round(self.x, 4),
            "y": round(self.y, 4),
            "vx": round(self.vx, 4),
            "vy": round(self.vy, 4),
            "age_seconds": round(self.age_seconds, 4),
            "type": self.particle_type.name,
        }


@dataclass(frozen=True)
class MemoryReport:
    """Statistics showing the memory economy gained from the Flyweight pattern."""

    total_particles: int
    unique_flyweights: int
    flyweight_names: tuple[str, ...]
    estimated_bytes_without_flyweight: int
    estimated_bytes_with_flyweight: int

    @property
    def memory_saved_bytes(self) -> int:
        """Return the estimated number of bytes saved by sharing flyweights."""
        return (
            self.estimated_bytes_without_flyweight - self.estimated_bytes_with_flyweight
        )

    @property
    def savings_percentage(self) -> float:
        """Return memory savings as a percentage of the unshared baseline."""
        if self.estimated_bytes_without_flyweight == 0:
            return 0.0
        return (self.memory_saved_bytes / self.estimated_bytes_without_flyweight) * 100
