"""Shared pytest fixtures for the Infrastructure Profile Cloner test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infra_profile.domain.entities import InfrastructureProfile, StorageConfig
from src.infra_profile.infrastructure.json_repository import JsonProfileRepository
from src.infra_profile.infrastructure.registry import ProfileRegistry


@pytest.fixture
def sample_profile() -> InfrastructureProfile:
    """A representative profile with non-empty nested collections."""
    return InfrastructureProfile(
        name="prod-api-template",
        instance_type="m5.xlarge",
        region="us-east-1",
        tags={"environment": "production"},
        firewall_rules=["allow-443-from-alb"],
        env_vars={"LOG_LEVEL": "INFO"},
        storage=StorageConfig(volume_type="ssd", size_gb=100, encrypted=True),
    )


@pytest.fixture
def registry(sample_profile: InfrastructureProfile) -> ProfileRegistry:
    """A registry pre-loaded with a single sample template."""
    reg = ProfileRegistry()
    reg.register(sample_profile)
    return reg


@pytest.fixture
def repository(tmp_path: Path) -> JsonProfileRepository:
    """A JSON repository backed by a temp file, isolated per test."""
    return JsonProfileRepository(tmp_path / "profiles.json")
