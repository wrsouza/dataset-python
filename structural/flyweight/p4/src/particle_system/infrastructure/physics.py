"""Concrete physics implementations for particle motion.

Each class implements `PhysicsProtocol` (domain/interfaces.py) so the
simulation use case can depend on the abstraction and swap physics models
freely — this is the Dependency Inversion boundary requested by the brief.
"""

from __future__ import annotations

from particle_system.domain.entities import Particle

EARTH_GRAVITY_PIXELS_PER_SECOND_SQUARED = 98.0


class SimpleGravityPhysics:
    """Applies constant downward gravity and per-type drag to particles."""

    def __init__(
        self, gravity: float = EARTH_GRAVITY_PIXELS_PER_SECOND_SQUARED
    ) -> None:
        self._gravity = gravity

    def step(self, particle: Particle, delta_seconds: float) -> None:
        """Advance position via velocity, apply gravity and drag, and age it."""
        drag = particle.particle_type.drag_coefficient
        particle.vy += self._gravity * delta_seconds
        particle.vx *= 1.0 - drag * delta_seconds
        particle.vy *= 1.0 - drag * delta_seconds

        particle.x += particle.vx * delta_seconds
        particle.y += particle.vy * delta_seconds
        particle.age_seconds += delta_seconds


class WeightlessPhysics:
    """Moves particles in a straight line with no gravity — e.g. zero-G FX."""

    def step(self, particle: Particle, delta_seconds: float) -> None:
        """Advance position by velocity only, with no gravitational pull."""
        particle.x += particle.vx * delta_seconds
        particle.y += particle.vy * delta_seconds
        particle.age_seconds += delta_seconds
