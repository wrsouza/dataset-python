"""Shared pytest fixtures for the Report Generation Template tests."""

from __future__ import annotations

import pytest
from flask.testing import FlaskClient

from report_generation_template.app import create_app
from report_generation_template.infrastructure.repository import (
    InMemoryReportRepository,
)


@pytest.fixture
def repository() -> InMemoryReportRepository:
    return InMemoryReportRepository()


@pytest.fixture
def client(repository: InMemoryReportRepository) -> FlaskClient:
    app = create_app(repository=repository)
    app.config.update(TESTING=True)
    return app.test_client()
