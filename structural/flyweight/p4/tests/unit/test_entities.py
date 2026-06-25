"""Tests for Particle (Context) and ParticleType (Flyweight) entities."""

from __future__ import annotations

from particle_system.domain.entities import MemoryReport, Particle, ParticleType


def _make_fire_type() -> ParticleType:
    return ParticleType(
        name="fire",
        sprite="sprites/fire.png",
        color="#FF4500",
        base_lifetime_seconds=1.0,
        drag_coefficient=0.05,
    )


def test_different_particles_share_same_particle_type_but_have_distinct_state() -> None:
    fire_type = _make_fire_type()

    particle_a = Particle(
        x=0.0, y=0.0, vx=1.0, vy=1.0, age_seconds=0.0, particle_type=fire_type
    )
    particle_b = Particle(
        x=10.0, y=20.0, vx=-1.0, vy=2.0, age_seconds=0.5, particle_type=fire_type
    )

    assert particle_a.particle_type is particle_b.particle_type
    assert particle_a.x != particle_b.x
    assert particle_a.age_seconds != particle_b.age_seconds


def test_type_name_delegates_to_particle_type() -> None:
    particle = Particle(
        x=0.0, y=0.0, vx=0.0, vy=0.0, age_seconds=0.0, particle_type=_make_fire_type()
    )

    assert particle.type_name == "fire"


def test_is_alive_true_when_age_below_lifetime() -> None:
    particle = Particle(
        x=0.0, y=0.0, vx=0.0, vy=0.0, age_seconds=0.5, particle_type=_make_fire_type()
    )

    assert particle.is_alive() is True


def test_is_alive_false_when_age_exceeds_lifetime() -> None:
    particle = Particle(
        x=0.0, y=0.0, vx=0.0, vy=0.0, age_seconds=5.0, particle_type=_make_fire_type()
    )

    assert particle.is_alive() is False


def test_to_dict_contains_only_extrinsic_state_and_type_name() -> None:
    particle = Particle(
        x=1.5, y=2.5, vx=3.0, vy=-4.0, age_seconds=0.25, particle_type=_make_fire_type()
    )

    serialized = particle.to_dict()

    assert serialized["x"] == 1.5
    assert serialized["type"] == "fire"
    assert "sprite" not in serialized
    assert "color" not in serialized


def test_memory_report_computes_savings() -> None:
    report = MemoryReport(
        total_particles=1000,
        unique_flyweights=3,
        flyweight_names=("fire", "spark", "smoke"),
        estimated_bytes_without_flyweight=512_000,
        estimated_bytes_with_flyweight=96_768,
    )

    assert report.memory_saved_bytes == 512_000 - 96_768
    assert report.savings_percentage > 0


def test_memory_report_zero_baseline_has_zero_percent_savings() -> None:
    report = MemoryReport(
        total_particles=0,
        unique_flyweights=0,
        flyweight_names=(),
        estimated_bytes_without_flyweight=0,
        estimated_bytes_with_flyweight=0,
    )

    assert report.savings_percentage == 0.0
