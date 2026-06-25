"""Shared test fixtures for P1 — SQL Query Builder."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from query_builder.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
