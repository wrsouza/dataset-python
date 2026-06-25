"""Application use cases orchestrating the particle simulation.

These use cases depend only on `ParticleTypeFactoryABC` and
`PhysicsProtocol` (domain/interfaces.py) — never on a concrete factory or
physics implementation. This is the Dependency Inversion boundary that lets
callers swap `SimpleGravityPhysics` for `WeightlessPhysics` (or any future
physics model) without touching this module.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from particle_system.domain.entities import MemoryReport, Particle
from particle_system.domain.interfaces import ParticleTypeFactoryABC, PhysicsProtocol
from particle_system.infrastructure.factory import ParticleTypeFactory

DEFAULT_SPAWN_RADIUS = 5.0
DEFAULT_SPEED_RANGE = (-50.0, 50.0)


class SpawnExplosionUseCase:
    """Creates N particles distributed across the given particle type names.

    Every particle gets fresh extrinsic state (position, velocity, age) but
    particles of the same type share the exact same `ParticleType` object —
    the core Flyweight guarantee demonstrated end-to-end here.
    """

    def __init__(self, factory: ParticleTypeFactoryABC) -> None:
        self._factory = factory

    def execute(
        self,
        count: int,
        type_names: list[str],
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        rng: random.Random | None = None,
    ) -> list[Particle]:
        """Spawn `count` particles spread across `type_names`."""
        generator = rng or random.Random()
        particles: list[Particle] = []
        for index in range(count):
            type_name = type_names[index % len(type_names)]
            particle_type = self._factory.get_or_create(type_name)
            particles.append(
                Particle(
                    x=origin_x
                    + generator.uniform(-DEFAULT_SPAWN_RADIUS, DEFAULT_SPAWN_RADIUS),
                    y=origin_y
                    + generator.uniform(-DEFAULT_SPAWN_RADIUS, DEFAULT_SPAWN_RADIUS),
                    vx=generator.uniform(*DEFAULT_SPEED_RANGE),
                    vy=generator.uniform(*DEFAULT_SPEED_RANGE),
                    age_seconds=0.0,
                    particle_type=particle_type,
                )
            )
        return particles


class RunSimulationUseCase:
    """Advances a list of particles through N physics steps, dropping dead ones.

    DIP: depends on `PhysicsProtocol`, so gravity, drag, or any other motion
    model can be injected without changing this use case.
    """

    def __init__(self, physics: PhysicsProtocol) -> None:
        self._physics = physics

    def execute(
        self, particles: list[Particle], steps: int, delta_seconds: float
    ) -> list[Particle]:
        """Run `steps` physics ticks of `delta_seconds` each; return survivors."""
        for _ in range(steps):
            for particle in particles:
                self._physics.step(particle, delta_seconds)
            particles = [p for p in particles if p.is_alive()]
        return particles


class GenerateMemoryReportUseCase:
    """Computes the Flyweight memory economy for a population of particles."""

    def __init__(self, factory: ParticleTypeFactory) -> None:
        self._factory = factory

    def execute(self, particles: list[Particle]) -> MemoryReport:
        """Build a `MemoryReport` comparing shared vs. duplicated intrinsic state."""
        total_particles = len(particles)
        return MemoryReport(
            total_particles=total_particles,
            unique_flyweights=self._factory.get_flyweight_count(),
            flyweight_names=self._factory.get_cached_names(),
            estimated_bytes_without_flyweight=(
                self._factory.estimate_bytes_without_flyweight(total_particles)
            ),
            estimated_bytes_with_flyweight=(
                self._factory.estimate_bytes_with_flyweight(total_particles)
            ),
        )


class ExportSimulationStateUseCase:
    """Serializes the current particle population to a JSON file."""

    def execute(self, particles: list[Particle], output_path: Path) -> int:
        """Write `particles` as JSON to `output_path`; return the particle count."""
        payload = [particle.to_dict() for particle in particles]
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return len(payload)
