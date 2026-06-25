"""Integration tests for the Typer CLI using CliRunner end-to-end."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from cli.main import LAST_RUN_STATE_PATH, app

runner = CliRunner()


def _cleanup_state_file() -> None:
    if LAST_RUN_STATE_PATH.exists():
        LAST_RUN_STATE_PATH.unlink()


def test_simulate_command_reports_particle_counts() -> None:
    _cleanup_state_file()
    result = runner.invoke(app, ["simulate", "--particles", "500", "--steps", "10"])

    assert result.exit_code == 0
    assert "Spawned 500 particles" in result.stdout
    assert "Unique ParticleType flyweights in cache: 3" in result.stdout
    _cleanup_state_file()


def test_simulate_then_stats_shows_memory_economy() -> None:
    _cleanup_state_file()
    runner.invoke(app, ["simulate", "--particles", "1000", "--steps", "5"])

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "Unique flyweights:    3" in result.stdout
    assert "Bytes saved" in result.stdout
    _cleanup_state_file()


def test_stats_without_prior_simulation_fails() -> None:
    _cleanup_state_file()
    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 1
    assert "Run `simulate` first" in result.output


def test_simulate_then_export_writes_json_file(tmp_path: Path) -> None:
    _cleanup_state_file()
    runner.invoke(app, ["simulate", "--particles", "20", "--steps", "5"])

    output_path = tmp_path / "particles.json"
    result = runner.invoke(app, ["export", str(output_path)])

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Exported" in result.stdout
    _cleanup_state_file()


def test_export_without_prior_simulation_fails(tmp_path: Path) -> None:
    _cleanup_state_file()
    output_path = tmp_path / "particles.json"
    result = runner.invoke(app, ["export", str(output_path)])

    assert result.exit_code == 1


def test_simulate_with_weightless_physics_runs_successfully() -> None:
    _cleanup_state_file()
    result = runner.invoke(
        app,
        ["simulate", "--particles", "100", "--steps", "5", "--physics", "weightless"],
    )

    assert result.exit_code == 0
    assert "weightless" in result.stdout
    _cleanup_state_file()
