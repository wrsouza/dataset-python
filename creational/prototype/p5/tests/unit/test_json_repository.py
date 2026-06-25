"""Unit tests for JsonProfileRepository."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.infra_profile.domain.entities import InfrastructureProfile
from src.infra_profile.infrastructure.json_repository import JsonProfileRepository


def test_get_returns_none_when_file_missing(tmp_path: Path) -> None:
    repo = JsonProfileRepository(tmp_path / "missing.json")

    assert repo.get("anything") is None


def test_save_then_get_round_trips_profile(
    repository: JsonProfileRepository, sample_profile: InfrastructureProfile
) -> None:
    repository.save(sample_profile)

    fetched = repository.get(sample_profile.name)

    assert fetched == sample_profile
    assert fetched is not sample_profile


def test_save_overwrites_existing_entry_with_same_name(
    repository: JsonProfileRepository, sample_profile: InfrastructureProfile
) -> None:
    repository.save(sample_profile)
    updated = sample_profile.clone()
    updated.region = "eu-central-1"

    repository.save(updated)

    fetched = repository.get(sample_profile.name)
    assert fetched is not None
    assert fetched.region == "eu-central-1"


def test_list_all_returns_every_saved_profile_sorted_by_name(
    repository: JsonProfileRepository, sample_profile: InfrastructureProfile
) -> None:
    other = sample_profile.clone()
    other.apply_overrides(name="aaa-profile")
    repository.save(sample_profile)
    repository.save(other)

    names = [profile.name for profile in repository.list_all()]

    assert names == ["aaa-profile", "prod-api-template"]


def test_list_all_returns_empty_list_when_no_file(tmp_path: Path) -> None:
    repo = JsonProfileRepository(tmp_path / "missing.json")

    assert repo.list_all() == []


def test_get_returns_none_when_file_is_empty(tmp_path: Path) -> None:
    file_path = tmp_path / "profiles.json"
    file_path.write_text("", encoding="utf-8")
    repo = JsonProfileRepository(file_path)

    assert repo.get("anything") is None


def test_get_raises_when_storage_is_malformed(tmp_path: Path) -> None:
    file_path = tmp_path / "profiles.json"
    file_path.write_text(
        '{"bad": {"name": "bad", "instance_type": "t3.micro", "region": "us-east-1",'
        ' "tags": {}, "firewall_rules": [], "env_vars": {},'
        ' "storage": "not-an-object"}}',
        encoding="utf-8",
    )
    repo = JsonProfileRepository(file_path)

    with pytest.raises(ValueError, match="storage"):
        repo.get("bad")


def test_get_raises_when_tags_are_malformed(tmp_path: Path) -> None:
    file_path = tmp_path / "profiles.json"
    file_path.write_text(
        '{"bad": {"name": "bad", "instance_type": "t3.micro", "region": "us-east-1",'
        ' "tags": "not-an-object", "firewall_rules": [], "env_vars": {},'
        ' "storage": {"volume_type": "ssd", "size_gb": 20, "encrypted": true}}}',
        encoding="utf-8",
    )
    repo = JsonProfileRepository(file_path)

    with pytest.raises(ValueError, match="tags"):
        repo.get("bad")


def test_get_raises_when_firewall_rules_are_malformed(tmp_path: Path) -> None:
    file_path = tmp_path / "profiles.json"
    file_path.write_text(
        '{"bad": {"name": "bad", "instance_type": "t3.micro", "region": "us-east-1",'
        ' "tags": {}, "firewall_rules": "not-a-list", "env_vars": {},'
        ' "storage": {"volume_type": "ssd", "size_gb": 20, "encrypted": true}}}',
        encoding="utf-8",
    )
    repo = JsonProfileRepository(file_path)

    with pytest.raises(ValueError, match="firewall_rules"):
        repo.get("bad")
