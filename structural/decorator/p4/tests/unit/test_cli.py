"""Testes unitários do CLI Typer (process-order)."""

from __future__ import annotations

from typer.testing import CliRunner

from observability.cli import app

runner = CliRunner()


def test_process_order_command_succeeds(moto_aws: None) -> None:
    result = runner.invoke(
        app,
        [
            "--customer-id",
            "c1",
            "--item-sku",
            "sku1",
            "--quantity",
            "2",
            "--unit-price",
            "10.0",
        ],
    )

    assert result.exit_code == 0
    assert "processado" in result.stdout


def test_process_order_command_fails_for_invalid_quantity(moto_aws: None) -> None:
    result = runner.invoke(
        app,
        [
            "--customer-id",
            "c1",
            "--item-sku",
            "sku1",
            "--quantity",
            "5000",
            "--unit-price",
            "10.0",
        ],
    )

    assert result.exit_code == 1
    assert "inválido" in result.stdout
