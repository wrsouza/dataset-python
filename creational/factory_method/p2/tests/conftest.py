"""Shared test fixtures for P2 — File Storage Factory."""
from __future__ import annotations

import tempfile

import pytest

from storage.infrastructure.creators import (
    GCSStorageFactory,
    LocalStorageFactory,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for LocalStorageClient tests."""
    return str(tmp_path)


@pytest.fixture
def local_factory(temp_dir: str) -> LocalStorageFactory:
    return LocalStorageFactory(base_dir=temp_dir)


@pytest.fixture
def gcs_factory() -> GCSStorageFactory:
    factory = GCSStorageFactory(bucket="test-bucket")
    # Reset shared state between tests
    from storage.infrastructure.creators import GCSStorageClient
    GCSStorageClient._store.clear()
    return factory


@pytest.fixture
def sample_data() -> bytes:
    return b"Hello, Factory Method Storage!"
