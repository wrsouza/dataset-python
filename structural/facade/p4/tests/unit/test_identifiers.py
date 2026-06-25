"""Tests for SQL identifier validation."""

from __future__ import annotations

import pytest

from migration.infrastructure.identifiers import (
    InvalidTableNameError,
    validate_table_name,
)


def test_accepts_valid_identifier() -> None:
    assert validate_table_name("orders") == "orders"
    assert validate_table_name("_orders_2") == "_orders_2"


@pytest.mark.parametrize(
    "bad_name",
    ["orders;DROP TABLE x", "orders--", "1orders", "orders table", ""],
)
def test_rejects_invalid_identifier(bad_name: str) -> None:
    with pytest.raises(InvalidTableNameError):
        validate_table_name(bad_name)
