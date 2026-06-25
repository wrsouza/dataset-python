"""Integration tests for the Typer CLI, using a temporary SQLite file
per test and moto to fake AWS S3."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from download_manager_fsm.main import app

runner = CliRunner()

BUCKET_NAME = "my-bucket"
OBJECT_KEY = "file.zip"


@pytest.fixture
def env(tmp_path: Path) -> Iterator[dict[str, str]]:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET_NAME)
        client.put_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY, Body=b"x" * 1024)
        yield {
            "DOWNLOAD_MANAGER_DB_PATH": str(tmp_path / "download_manager.db"),
            "AWS_REGION": "us-east-1",
        }


def _s3_key() -> str:
    return f"{BUCKET_NAME}/{OBJECT_KEY}"


def test_start_then_status(env: dict[str, str]) -> None:
    runner.invoke(app, ["start", "job-1", _s3_key()], env=env)

    result = runner.invoke(app, ["status", "job-1"], env=env)

    assert "Downloading" in result.stdout


def test_pause_then_resume(env: dict[str, str]) -> None:
    runner.invoke(app, ["start", "job-1", _s3_key()], env=env)
    runner.invoke(app, ["pause", "job-1"], env=env)

    runner.invoke(app, ["resume", "job-1"], env=env)
    result = runner.invoke(app, ["status", "job-1"], env=env)

    assert "Downloading" in result.stdout


def test_complete_fetches_size_from_s3(env: dict[str, str]) -> None:
    runner.invoke(app, ["start", "job-1", _s3_key()], env=env)

    result = runner.invoke(app, ["complete", "job-1"], env=env)

    assert "1024 bytes" in result.stdout
    assert "Completed" in result.stdout


def test_fail_then_retry(env: dict[str, str]) -> None:
    runner.invoke(app, ["start", "job-1", _s3_key()], env=env)
    runner.invoke(app, ["fail", "job-1", "connection reset"], env=env)

    result = runner.invoke(app, ["retry", "job-1"], env=env)

    assert "Idle" in result.stdout


def test_invalid_transition_exits_with_error(env: dict[str, str]) -> None:
    runner.invoke(app, ["start", "job-1", _s3_key()], env=env)

    result = runner.invoke(app, ["resume", "job-1"], env=env)

    assert result.exit_code == 1
    assert "Cannot perform" in result.stdout


def test_status_for_unknown_job_exits_with_error(env: dict[str, str]) -> None:
    result = runner.invoke(app, ["status", "does-not-exist"], env=env)

    assert result.exit_code == 1
    assert "not found" in result.stdout
