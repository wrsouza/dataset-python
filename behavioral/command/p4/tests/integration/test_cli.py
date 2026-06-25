"""Integration tests for the Typer CLI, using a temporary SQLite file per test."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli_history.main import app

runner = CliRunner()


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    return {"CLI_HISTORY_DB_PATH": str(tmp_path / "cli_history.db")}


def test_add_then_list_shows_item(env: dict[str, str]) -> None:
    runner.invoke(app, ["add", "Buy milk"], env=env)

    result = runner.invoke(app, ["list"], env=env)

    assert "Buy milk" in result.stdout


def test_remove_takes_item_out_of_list(env: dict[str, str]) -> None:
    runner.invoke(app, ["add", "Buy milk"], env=env)
    runner.invoke(app, ["remove", "Buy milk"], env=env)

    result = runner.invoke(app, ["list"], env=env)

    assert "(empty)" in result.stdout


def test_undo_reverts_last_add(env: dict[str, str]) -> None:
    runner.invoke(app, ["add", "Buy milk"], env=env)

    result = runner.invoke(app, ["undo"], env=env)

    assert "(empty)" in result.stdout


def test_history_lists_every_executed_command(env: dict[str, str]) -> None:
    runner.invoke(app, ["add", "Buy milk"], env=env)
    runner.invoke(app, ["remove", "Buy milk"], env=env)

    result = runner.invoke(app, ["history"], env=env)

    assert "add" in result.stdout
    assert "remove" in result.stdout


def test_replay_rebuilds_state_matching_current_list(env: dict[str, str]) -> None:
    runner.invoke(app, ["add", "Buy milk"], env=env)
    runner.invoke(app, ["add", "Walk dog"], env=env)

    result = runner.invoke(app, ["replay"], env=env)

    assert "Buy milk" in result.stdout
    assert "Walk dog" in result.stdout
