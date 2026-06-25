"""Integration tests for the Typer CLI against a real temporary directory tree."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from file_tree_iterator.main import app

runner = CliRunner()


def _make_tree(root: Path) -> None:
    (root / "a.txt").write_text("hello")
    sub = root / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("world!")


def test_tree_command_lists_every_entry(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    result = runner.invoke(app, ["tree", str(tmp_path)])

    assert result.exit_code == 0
    assert "a.txt" in result.stdout
    assert "sub" in result.stdout
    assert "b.txt" in result.stdout


def test_summary_command_reports_counts_and_size(tmp_path: Path) -> None:
    _make_tree(tmp_path)

    result = runner.invoke(app, ["summary", str(tmp_path)])

    assert result.exit_code == 0
    assert "Files:       2" in result.stdout
    assert "Directories: 1" in result.stdout
    assert "Total size:  11 bytes" in result.stdout
