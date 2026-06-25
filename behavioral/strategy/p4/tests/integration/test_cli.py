"""Integration tests for the Typer CLI, using real temporary files per test."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from compression_strategy_cli.main import app

runner = CliRunner()


def test_compress_then_decompress_round_trip(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    original = b"the quick brown fox jumps over the lazy dog" * 10
    input_path.write_bytes(original)

    compress_result = runner.invoke(
        app, ["compress", str(input_path), "--strategy", "gzip"]
    )
    assert compress_result.exit_code == 0
    assert "ratio" in compress_result.stdout

    compressed_path = tmp_path / "data.txt.gz"
    assert compressed_path.exists()

    decompress_result = runner.invoke(
        app, ["decompress", str(compressed_path), "--strategy", "gzip"]
    )
    assert decompress_result.exit_code == 0
    assert (tmp_path / "data.txt").read_bytes() == original


def test_compress_with_unknown_strategy_exits_with_error(tmp_path: Path) -> None:
    input_path = tmp_path / "data.txt"
    input_path.write_bytes(b"data")

    result = runner.invoke(app, ["compress", str(input_path), "--strategy", "unknown"])

    assert result.exit_code == 1
    assert "Unknown compression strategy" in result.stdout


def test_list_strategies_prints_all_names() -> None:
    result = runner.invoke(app, ["list-strategies"])

    assert result.exit_code == 0
    assert "gzip" in result.stdout
    assert "bz2" in result.stdout
