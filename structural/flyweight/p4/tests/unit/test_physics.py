"""Tests for the concrete PhysicsProtocol implementations."""

from __future__ import annotations

from particle_system.domain.entities import Particle, ParticleType
from particle_system.infrastructure.physics import (
    SimpleGravityPhysics,
    WeightlessPhysics,
)


def _make_particle() -> Particle:
    particle_type = ParticleType(
        name="fire",
        sprite="sprites/fire.png",
        color="#FF4500",
        base_lifetime_seconds=5.0,
        drag_coefficient=0.1,
    )
    return Particle(
        x=0.0, y=0.0, vx=10.0, vy=0.0, age_seconds=0.0, particle_type=particle_type
    )


def test_simple_gravity_physics_increases_downward_velocity() -> None:
    particle = _make_particle()
    physics = SimpleGravityPhysics(gravity=100.0)

    physics.step(particle, delta_seconds=0.1)

    assert particle.vy > 0.0


def test_simple_gravity_physics_advances_position_and_age() -> None:
    particle = _make_particle()
    physics = SimpleGravityPhysics(gravity=100.0)

    physics.step(particle, delta_seconds=0.1)

    assert particle.x != 0.0
    assert particle.age_seconds == 0.1


def test_simple_gravity_physics_applies_drag_to_horizontal_velocity() -> None:
    particle = _make_particle()
    physics = SimpleGravityPhysics(gravity=0.0)
    initial_vx = particle.vx

    physics.step(particle, delta_seconds=1.0)

    assert particle.vx < initial_vx


def test_weightless_physics_does_not_change_velocity() -> None:
    particle = _make_particle()
    physics = WeightlessPhysics()

    physics.step(particle, delta_seconds=0.1)

    assert particle.vx == 10.0
    assert particle.vy == 0.0


def test_weightless_physics_advances_position_and_age() -> None:
    particle = _make_particle()
    physics = WeightlessPhysics()

    physics.step(particle, delta_seconds=0.5)

    assert particle.x == 5.0
    assert particle.age_seconds == 0.5
