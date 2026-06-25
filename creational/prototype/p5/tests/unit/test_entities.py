"""Unit tests for InfrastructureProfile, focused on deep-clone correctness."""

from __future__ import annotations

import pytest

from src.infra_profile.domain.entities import InfrastructureProfile, StorageConfig


def test_clone_returns_equal_but_distinct_object(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    assert cloned == sample_profile
    assert cloned is not sample_profile


def test_mutating_clone_tags_does_not_affect_original(
    sample_profile: InfrastructureProfile,
) -> None:
    """The single most important Prototype guarantee: no shared mutable state."""
    cloned = sample_profile.clone()

    cloned.tags["environment"] = "staging"
    cloned.tags["new_key"] = "new_value"

    assert sample_profile.tags == {"environment": "production"}
    assert cloned.tags == {"environment": "staging", "new_key": "new_value"}


def test_mutating_clone_firewall_rules_does_not_affect_original(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    cloned.firewall_rules.append("allow-22-from-bastion")

    assert sample_profile.firewall_rules == ["allow-443-from-alb"]
    assert cloned.firewall_rules == ["allow-443-from-alb", "allow-22-from-bastion"]


def test_mutating_clone_env_vars_does_not_affect_original(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    cloned.env_vars["LOG_LEVEL"] = "DEBUG"

    assert sample_profile.env_vars == {"LOG_LEVEL": "INFO"}
    assert cloned.env_vars == {"LOG_LEVEL": "DEBUG"}


def test_mutating_clone_storage_does_not_affect_original(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    cloned.storage.size_gb = 500

    assert sample_profile.storage.size_gb == 100
    assert cloned.storage.size_gb == 500
    assert cloned.storage is not sample_profile.storage


def test_apply_overrides_changes_only_given_fields(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    cloned.apply_overrides(name="staging-api-template", region="us-west-2")

    assert cloned.name == "staging-api-template"
    assert cloned.region == "us-west-2"
    assert cloned.instance_type == sample_profile.instance_type


def test_apply_overrides_rejects_unknown_field(
    sample_profile: InfrastructureProfile,
) -> None:
    cloned = sample_profile.clone()

    with pytest.raises(AttributeError, match="does_not_exist"):
        cloned.apply_overrides(does_not_exist="x")


def test_storage_config_default_size() -> None:
    storage = StorageConfig()

    assert storage.size_gb == 20
    assert storage.encrypted is True
