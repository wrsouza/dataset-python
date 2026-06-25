"""Integration tests for the Typer CLI, using a temporary SQLite file per test."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from text_editor_memento.main import app

runner = CliRunner()


@pytest.fixture
def env(tmp_path: Path) -> dict[str, str]:
    return {"TEXT_EDITOR_DB_PATH": str(tmp_path / "text_editor.db")}


def test_write_then_show(env: dict[str, str]) -> None:
    runner.invoke(app, ["write", "Hello, world"], env=env)

    result = runner.invoke(app, ["show"], env=env)

    assert "Hello, world" in result.stdout


def test_show_before_any_write_is_empty(env: dict[str, str]) -> None:
    result = runner.invoke(app, ["show"], env=env)

    assert "(empty)" in result.stdout


def test_undo_reverts_to_previous_write(env: dict[str, str]) -> None:
    runner.invoke(app, ["write", "first"], env=env)
    runner.invoke(app, ["write", "second"], env=env)

    runner.invoke(app, ["undo"], env=env)
    result = runner.invoke(app, ["show"], env=env)

    assert "first" in result.stdout


def test_undo_without_history_exits_with_error(env: dict[str, str]) -> None:
    result = runner.invoke(app, ["undo"], env=env)

    assert result.exit_code == 1
    assert "Nothing to undo" in result.stdout


def test_redo_reapplies_undone_write(env: dict[str, str]) -> None:
    runner.invoke(app, ["write", "first"], env=env)
    runner.invoke(app, ["write", "second"], env=env)
    runner.invoke(app, ["undo"], env=env)

    runner.invoke(app, ["redo"], env=env)
    result = runner.invoke(app, ["show"], env=env)

    assert "second" in result.stdout


def test_redo_without_history_exits_with_error(env: dict[str, str]) -> None:
    runner.invoke(app, ["write", "first"], env=env)

    result = runner.invoke(app, ["redo"], env=env)

    assert result.exit_code == 1
    assert "Nothing to redo" in result.stdout


def test_history_lists_every_snapshot(env: dict[str, str]) -> None:
    runner.invoke(app, ["write", "first"], env=env)
    runner.invoke(app, ["write", "second"], env=env)

    result = runner.invoke(app, ["history"], env=env)

    assert "first" in result.stdout
    assert "second" in result.stdout
