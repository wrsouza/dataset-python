"""Tests for the application use cases."""

from __future__ import annotations

import random
from pathlib import Path

from particle_system.application.use_cases import (
    ExportSimulationStateUseCase,
    GenerateMemoryReportUseCase,
    RunSimulationUseCase,
    SpawnExplosionUseCase,
)
from particle_system.infrastructure.factory import ParticleTypeFactory
from particle_system.infrastructure.physics import (
    SimpleGravityPhysics,
    WeightlessPhysics,
)


class TestSpawnExplosionUseCase:
    def test_spawns_requested_number_of_particles(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        use_case = SpawnExplosionUseCase(factory=factory)

        particles = use_case.execute(count=50, type_names=["fire", "spark"], rng=rng)

        assert len(particles) == 50

    def test_particles_of_same_type_share_flyweight(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        use_case = SpawnExplosionUseCase(factory=factory)

        particles = use_case.execute(count=10, type_names=["fire"], rng=rng)

        first_type = particles[0].particle_type
        assert all(p.particle_type is first_type for p in particles)

    def test_only_few_flyweights_created_for_many_particles(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        use_case = SpawnExplosionUseCase(factory=factory)

        use_case.execute(count=5000, type_names=["fire", "spark", "smoke"], rng=rng)

        assert factory.get_flyweight_count() == 3


class TestRunSimulationUseCase:
    def test_gravity_physics_eventually_kills_short_lived_particles(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        spawn_use_case = SpawnExplosionUseCase(factory=factory)
        particles = spawn_use_case.execute(count=20, type_names=["spark"], rng=rng)

        run_use_case = RunSimulationUseCase(physics=SimpleGravityPhysics())
        survivors = run_use_case.execute(particles, steps=100, delta_seconds=0.1)

        assert len(survivors) < len(particles)

    def test_weightless_physics_preserves_particle_count_when_lifetime_is_long(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        spawn_use_case = SpawnExplosionUseCase(factory=factory)
        particles = spawn_use_case.execute(count=10, type_names=["smoke"], rng=rng)

        run_use_case = RunSimulationUseCase(physics=WeightlessPhysics())
        survivors = run_use_case.execute(particles, steps=3, delta_seconds=0.1)

        assert len(survivors) == 10


class TestGenerateMemoryReportUseCase:
    def test_report_reflects_unique_flyweights_versus_total_particles(
        self, factory: ParticleTypeFactory, rng: random.Random
    ) -> None:
        spawn_use_case = SpawnExplosionUseCase(factory=factory)
        particles = spawn_use_case.execute(
            count=1000, type_names=["fire", "spark", "smoke"], rng=rng
        )

        report_use_case = GenerateMemoryReportUseCase(factory=factory)
        report = report_use_case.execute(particles)

        assert report.total_particles == 1000
        assert report.unique_flyweights == 3
        assert report.memory_saved_bytes > 0


class TestExportSimulationStateUseCase:
    def test_exports_particles_as_json(
        self, factory: ParticleTypeFactory, rng: random.Random, tmp_path: Path
    ) -> None:
        spawn_use_case = SpawnExplosionUseCase(factory=factory)
        particles = spawn_use_case.execute(count=5, type_names=["fire"], rng=rng)

        export_use_case = ExportSimulationStateUseCase()
        output_path = tmp_path / "export.json"
        count = export_use_case.execute(particles, output_path)

        assert count == 5
        assert output_path.exists()
        assert "fire" in output_path.read_text(encoding="utf-8")
