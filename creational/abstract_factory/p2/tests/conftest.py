"""Shared pytest fixtures for the Cloud Storage Factory test suite."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cloud_storage.infrastructure.factories import (
    AzureStorageFactory,
    GCSStorageFactory,
)


@pytest.fixture
def gcs_factory() -> GCSStorageFactory:
    """Fresh GCS factory for each test — in-memory, no side effects."""
    return GCSStorageFactory()


@pytest.fixture
def azure_factory() -> AzureStorageFactory:
    """Fresh Azure factory for each test — in-memory, no side effects."""
    return AzureStorageFactory()


@pytest.fixture
def test_client() -> TestClient:
    """FastAPI test client using the real app with GCS/Azure (no LocalStack)."""
    from cloud_storage.app import app
    return TestClient(app)
