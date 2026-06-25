"""Integration tests for the Typer CLI using CliRunner end-to-end."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from src.cli.main import app

runner = CliRunner()


def test_run_command_executes_full_definition_file_successfully(
    example_definition_path: Path,
) -> None:
    result = runner.invoke(app, ["run", str(example_definition_path)])

    assert result.exit_code == 0
    assert "build_all" in result.stdout
    assert "SUCCESS" in result.stdout


def test_run_command_prints_nested_task_results(
    example_definition_path: Path,
) -> None:
    result = runner.invoke(app, ["run", str(example_definition_path)])

    assert "test_all" in result.stdout
    assert "unit_tests" in result.stdout
    assert "integration_tests" in result.stdout


def test_run_command_fails_when_a_leaf_task_fails(tmp_path: Path) -> None:
    definition_path = tmp_path / "failing.yml"
    definition_path.write_text(
        "type: group\n"
        "name: build_all\n"
        "tasks:\n"
        "  - type: simulated\n"
        "    name: compile\n"
        "    should_succeed: false\n"
    )

    result = runner.invoke(app, ["run", str(definition_path)])

    assert result.exit_code == 1
    assert "FAILURE" in result.stdout


def test_run_command_reports_error_for_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.yml"

    result = runner.invoke(app, ["run", str(missing_path)])

    assert result.exit_code != 0


def test_describe_command_shows_estimated_duration(
    example_definition_path: Path,
) -> None:
    result = runner.invoke(app, ["describe", str(example_definition_path)])

    assert result.exit_code == 0
    assert "build_all" in result.stdout
    assert "estimated" in result.stdout


def test_describe_command_reports_error_for_invalid_definition(
    tmp_path: Path,
) -> None:
    bad_path = tmp_path / "bad.yml"
    bad_path.write_text("type: mystery\nname: oops\n")

    result = runner.invoke(app, ["describe", str(bad_path)])

    assert result.exit_code == 1
