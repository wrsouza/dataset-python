"""Integration tests for the Typer CLI using CliRunner end-to-end."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from src.infra_profile.infrastructure.cli import app

runner = CliRunner()


def test_list_templates_command_prints_default_templates() -> None:
    result = runner.invoke(app, ["list-templates"])

    assert result.exit_code == 0
    assert "prod-api-template" in result.stdout
    assert "staging-db-template" in result.stdout


def test_clone_command_creates_and_persists_new_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(
        app,
        [
            "clone",
            "prod-api-template",
            "staging-api-template",
            "--region",
            "us-west-2",
        ],
    )

    assert result.exit_code == 0
    assert profiles_file.exists()
    assert "staging-api-template" in result.stdout


def test_show_command_prints_fields_for_existing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))
    runner.invoke(app, ["clone", "prod-api-template", "staging-api-template"])

    result = runner.invoke(app, ["show", "staging-api-template"])

    assert result.exit_code == 0
    assert "instance_type" in result.stdout


def test_show_command_fails_for_missing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(app, ["show", "does-not-exist"])

    assert result.exit_code != 0


def test_create_command_persists_brand_new_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(
        app,
        ["create", "dev-box", "--instance-type", "t3.micro", "--region", "us-east-1"],
    )

    assert result.exit_code == 0
    assert "dev-box" in result.stdout


def test_list_command_shows_saved_profiles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))
    runner.invoke(
        app,
        ["create", "dev-box", "--instance-type", "t3.micro", "--region", "us-east-1"],
    )

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "dev-box" in result.stdout


def test_export_command_writes_standalone_json_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))
    runner.invoke(app, ["clone", "prod-api-template", "staging-api-template"])
    export_path = tmp_path / "exported.json"

    result = runner.invoke(
        app, ["export", "staging-api-template", "--output", str(export_path)]
    )

    assert result.exit_code == 0
    assert export_path.exists()


def test_clone_command_accepts_instance_type_and_tag_overrides(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(
        app,
        [
            "clone",
            "prod-api-template",
            "custom-api",
            "--instance-type",
            "m5.large",
            "--tag",
            "owner=team-x",
        ],
    )

    assert result.exit_code == 0


def test_clone_command_rejects_malformed_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(
        app, ["clone", "prod-api-template", "x", "--tag", "not-a-pair"]
    )

    assert result.exit_code != 0


def test_export_command_fails_for_missing_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(
        app, ["export", "does-not-exist", "--output", str(tmp_path / "out.json")]
    )

    assert result.exit_code != 0


def test_create_command_rejects_duplicate_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))
    runner.invoke(
        app,
        ["create", "dev-box", "--instance-type", "t3.micro", "--region", "us-east-1"],
    )

    result = runner.invoke(
        app,
        ["create", "dev-box", "--instance-type", "t3.micro", "--region", "us-east-1"],
    )

    assert result.exit_code != 0


def test_clone_command_rejects_unknown_template(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    profiles_file = tmp_path / "profiles.json"
    monkeypatch.setenv("PROFILES_FILE_PATH", str(profiles_file))

    result = runner.invoke(app, ["clone", "does-not-exist", "new-profile"])

    assert result.exit_code != 0
