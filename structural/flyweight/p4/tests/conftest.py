"""Shared pytest fixtures for the particle system test suite."""

from __future__ import annotations

import random

import pytest

from particle_system.infrastructure.factory import ParticleTypeFactory


@pytest.fixture
def factory() -> ParticleTypeFactory:
    return ParticleTypeFactory()


@pytest.fixture
def rng() -> random.Random:
    return random.Random(1234)
