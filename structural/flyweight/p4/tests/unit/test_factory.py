"""Tests for ParticleTypeFactory — verifies Flyweight sharing (core guarantee)."""

from __future__ import annotations

import dataclasses

import pytest

from particle_system.domain.entities import ParticleType
from particle_system.infrastructure.factory import ParticleTypeFactory


def test_get_or_create_returns_same_instance_for_same_type(
    factory: ParticleTypeFactory,
) -> None:
    """Core Flyweight guarantee: same name -> same object reference."""
    fire_a = factory.get_or_create("fire")
    fire_b = factory.get_or_create("fire")

    assert fire_a is fire_b


def test_get_or_create_returns_different_instances_for_different_types(
    factory: ParticleTypeFactory,
) -> None:
    fire = factory.get_or_create("fire")
    smoke = factory.get_or_create("smoke")

    assert fire is not smoke


def test_flyweight_is_frozen(factory: ParticleTypeFactory) -> None:
    """ParticleType must be immutable."""
    particle_type = factory.get_or_create("spark")

    with pytest.raises(dataclasses.FrozenInstanceError):
        particle_type.color = "#000000"  # type: ignore[misc]


def test_default_types_have_expected_attributes(factory: ParticleTypeFactory) -> None:
    fire = factory.get_or_create("fire")
    smoke = factory.get_or_create("smoke")

    assert fire.color == "#FF4500"
    assert smoke.base_lifetime_seconds > fire.base_lifetime_seconds


def test_unknown_type_gets_fallback_definition(factory: ParticleTypeFactory) -> None:
    unknown = factory.get_or_create("totally_unknown_kind")

    assert unknown.name == "totally_unknown_kind"
    assert unknown.sprite == "sprites/unknown.png"


def test_unknown_type_is_cached_after_first_lookup(
    factory: ParticleTypeFactory,
) -> None:
    first = factory.get_or_create("ghost")
    second = factory.get_or_create("ghost")

    assert first is second


def test_get_flyweight_count_reflects_unique_types(
    factory: ParticleTypeFactory,
) -> None:
    initial = factory.get_flyweight_count()

    factory.get_or_create("fire")
    factory.get_or_create("fire")  # same type — no new flyweight
    assert factory.get_flyweight_count() == initial

    factory.get_or_create("brand_new_type")
    assert factory.get_flyweight_count() == initial + 1


def test_register_type_allows_new_kind_without_modifying_factory(
    factory: ParticleTypeFactory,
) -> None:
    """OCP: a new particle kind is added via registration, not by editing the class."""
    magic_spark = ParticleType(
        name="magic_spark",
        sprite="sprites/magic_spark.png",
        color="#9400D3",
        base_lifetime_seconds=0.8,
        drag_coefficient=0.01,
    )
    factory.register_type(magic_spark)

    resolved = factory.get_or_create("magic_spark")

    assert resolved is magic_spark


def test_get_cached_names_includes_registered_type(
    factory: ParticleTypeFactory,
) -> None:
    factory.get_or_create("fire")

    assert "fire" in factory.get_cached_names()


def test_estimate_bytes_with_flyweight_scales_with_unique_types_not_particles(
    factory: ParticleTypeFactory,
) -> None:
    factory.get_or_create("fire")
    factory.get_or_create("spark")
    factory.get_or_create("smoke")

    bytes_for_100 = factory.estimate_bytes_with_flyweight(100)
    bytes_for_1000 = factory.estimate_bytes_with_flyweight(1000)

    # The flyweight-shared portion is constant; only the extrinsic part grows.
    assert bytes_for_1000 > bytes_for_100
    assert factory.estimate_bytes_without_flyweight(1000) > bytes_for_1000
