"""Integration tests for the Typer CLI, using moto to fake AWS S3 and a
temporary SQLite file (MySQL stand-in) per test."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from data_processing_pipeline.main import app

runner = CliRunner()

BUCKET_NAME = "my-bucket"


@pytest.fixture
def env(tmp_path: Path) -> Iterator[dict[str, str]]:
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET_NAME)
        client.put_object(Bucket=BUCKET_NAME, Key="data.csv", Body=b"id,name\n1,Ana\n")
        client.put_object(
            Bucket=BUCKET_NAME, Key="data.jsonl", Body=b'{"id": 1, "name": "Ana"}\n'
        )
        yield {
            "AWS_REGION": "us-east-1",
            "DB_DIALECT": "sqlite",
            "DB_DSN": str(tmp_path / "processing.db"),
        }


def test_process_csv_command(env: dict[str, str]) -> None:
    result = runner.invoke(app, ["process-csv", BUCKET_NAME, "data.csv"], env=env)

    assert result.exit_code == 0
    assert "processed 1, persisted 1" in result.stdout


def test_process_json_command(env: dict[str, str]) -> None:
    result = runner.invoke(app, ["process-json", BUCKET_NAME, "data.jsonl"], env=env)

    assert result.exit_code == 0
    assert "processed 1, persisted 1" in result.stdout
