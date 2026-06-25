"""Unit tests for the Typer CLI commands."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from compose_builder.main import app

runner = CliRunner()


def test_list_presets_command_outputs_known_preset() -> None:
    result = runner.invoke(app, ["list-presets"])

    assert result.exit_code == 0
    assert "web-postgres-redis" in result.stdout


def test_print_command_outputs_yaml() -> None:
    result = runner.invoke(app, ["print", "--preset", "web-postgres-redis"])

    assert result.exit_code == 0
    assert "services:" in result.stdout


def test_print_command_unknown_preset_exits_nonzero() -> None:
    result = runner.invoke(app, ["print", "--preset", "nope"])

    assert result.exit_code == 1


def test_generate_command_writes_file(tmp_path: Path) -> None:
    output = tmp_path / "out.yml"

    result = runner.invoke(
        app, ["generate", "--preset", "web-postgres-redis", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert output.exists()
    assert "Wrote" in result.stdout


def test_generate_command_unknown_preset_exits_nonzero(tmp_path: Path) -> None:
    output = tmp_path / "out.yml"

    result = runner.invoke(
        app, ["generate", "--preset", "nope", "--output", str(output)]
    )

    assert result.exit_code == 1
