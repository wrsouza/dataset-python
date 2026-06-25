"""Unit tests for ProfileRegistry."""

from __future__ import annotations

import pytest

from src.infra_profile.domain.entities import InfrastructureProfile
from src.infra_profile.infrastructure.registry import (
    ProfileRegistry,
    TemplateNotFoundError,
    build_default_registry,
)


def test_register_and_get_template_round_trip(
    sample_profile: InfrastructureProfile,
) -> None:
    registry = ProfileRegistry()
    registry.register(sample_profile)

    fetched = registry.get_template(sample_profile.name)

    assert fetched is sample_profile


def test_get_template_raises_for_unknown_name() -> None:
    registry = ProfileRegistry()

    with pytest.raises(TemplateNotFoundError):
        registry.get_template("does-not-exist")


def test_list_template_names_is_sorted(sample_profile: InfrastructureProfile) -> None:
    registry = ProfileRegistry()
    registry.register(sample_profile)
    registry.register(
        InfrastructureProfile(
            name="aaa-template", instance_type="t3.micro", region="us-east-1"
        )
    )

    assert registry.list_template_names() == ["aaa-template", "prod-api-template"]


def test_register_extends_catalog_without_modifying_class() -> None:
    """Open/Closed: adding a new template is just another register() call."""
    registry = ProfileRegistry()
    new_profile = InfrastructureProfile(
        name="custom-template", instance_type="c5.large", region="eu-west-1"
    )

    registry.register(new_profile)

    assert registry.get_template("custom-template") is new_profile


def test_build_default_registry_has_expected_templates() -> None:
    registry = build_default_registry()

    names = registry.list_template_names()

    assert "prod-api-template" in names
    assert "staging-db-template" in names
