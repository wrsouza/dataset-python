"""Shared pytest fixtures for the E-commerce Order Facade test suite."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws


@pytest.fixture
def sqlite_database_url(tmp_path: Path) -> str:
    """SQLite file-based URL standing in for PostgreSQL in tests.

    Decision: real PostgreSQL is not guaranteed to be reachable when tests
    run outside docker-compose, so persistence tests exercise the same
    raw-SQL repository/service classes against SQLite. ``database.py``
    deliberately avoids PostgreSQL-only SQL (e.g. ``JSONB``, ``ON CONFLICT``)
    so the same schema and queries work identically on both engines.

    A file-based (rather than in-memory) SQLite database is used because
    ``TestClient`` dispatches requests on a worker thread, and SQLite
    in-memory connections are bound to the thread that created them.
    """
    return f"sqlite:///{tmp_path}/test.db"


@pytest.fixture
def sqs_queue_url() -> Iterator[str]:
    """A real (moto-mocked) SQS queue URL for notification service tests."""
    with mock_aws():
        client = boto3.client("sqs", region_name="us-east-1")
        response = client.create_queue(QueueName="orders")
        yield response["QueueUrl"]


@pytest.fixture
def client(sqlite_database_url: str) -> Iterator[TestClient]:
    """TestClient wired against the real FastAPI app.

    Decision: the app's lifespan (``src/main.py``) reads ``DATABASE_URL``
    from the environment and calls ``init_engine``/``create_tables`` against
    PostgreSQL by default. Setting ``DATABASE_URL`` to an in-memory SQLite
    URL *before* the ``TestClient`` context starts (which triggers the
    lifespan) redirects the same SQL schema/queries to SQLite — the raw SQL
    in ``infrastructure/database.py`` avoids PostgreSQL-only syntax for
    exactly this reason. AWS SQS is mocked with moto, so the full
    HTTP -> Facade -> subsystems flow is exercised without requiring
    docker-compose or real AWS credentials.
    """
    os.environ["DATABASE_URL"] = sqlite_database_url

    with mock_aws():
        sqs_client = boto3.client("sqs", region_name="us-east-1")
        queue = sqs_client.create_queue(QueueName="orders")
        os.environ["SQS_QUEUE_URL"] = queue["QueueUrl"]
        os.environ["AWS_ENDPOINT_URL"] = ""

        from src.main import app

        with TestClient(app) as test_client:
            yield test_client

    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("SQS_QUEUE_URL", None)
    os.environ.pop("AWS_ENDPOINT_URL", None)
