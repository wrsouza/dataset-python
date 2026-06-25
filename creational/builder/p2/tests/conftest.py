"""Shared test fixtures for P2 — Report Builder."""
from __future__ import annotations

import pytest

from report_builder.main import app


@pytest.fixture()
def client():  # type: ignore[no-untyped-def]
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture()
def sales_data() -> dict[str, object]:
    return {
        "period": "Q1 2024",
        "rows": [
            ["2024-01-15", "Alice", "Widget A", 3, 150.0],
            ["2024-02-20", "Bob", "Widget B", 1, 75.0],
        ],
        "total": 225.0,
    }


@pytest.fixture()
def inventory_data() -> dict[str, object]:
    return {
        "warehouse": "Warehouse 1",
        "rows": [
            ["SKU001", "Widget A", "Electronics", 50, 10],
            ["SKU002", "Widget B", "Electronics", 5, 10],
        ],
    }
