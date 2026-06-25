"""Integration tests for the Typer CLI, with boto3 patched to use moto's
in-memory S3 mock instead of contacting real AWS."""

from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from src.cli.main import app

runner = CliRunner()

CLI_BUCKET = "remote-file-proxy-cli-bucket"
CLI_KEY = "notes/todo.txt"
CLI_CONTENT = b"buy milk"


@pytest.fixture
def cli_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Run the CLI against a moto-mocked S3, with env vars pointing at it."""
    monkeypatch.setenv("S3_BUCKET", CLI_BUCKET)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.delenv("S3_ENDPOINT_URL", raising=False)
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=CLI_BUCKET)
        client.put_object(Bucket=CLI_BUCKET, Key=CLI_KEY, Body=CLI_CONTENT)
        yield


class TestReadCommand:
    def test_reads_existing_file(self, cli_env: None) -> None:
        result = runner.invoke(app, ["read", CLI_KEY])
        assert result.exit_code == 0
        assert str(len(CLI_CONTENT)) in result.stdout

    def test_missing_file_exits_nonzero(self, cli_env: None) -> None:
        result = runner.invoke(app, ["read", "missing.txt"])
        assert result.exit_code == 1
        assert "Error" in result.output


class TestCheckCommand:
    def test_existing_file_reports_exists(self, cli_env: None) -> None:
        result = runner.invoke(app, ["check", CLI_KEY])
        assert result.exit_code == 0
        assert "exists" in result.stdout

    def test_missing_file_reports_absence_and_exits_nonzero(
        self, cli_env: None
    ) -> None:
        result = runner.invoke(app, ["check", "missing.txt"])
        assert result.exit_code == 1
        assert "does not exist" in result.stdout


class TestStatsCommand:
    def test_reports_one_hit_one_miss_for_two_reads(self, cli_env: None) -> None:
        result = runner.invoke(app, ["stats", CLI_KEY])
        assert result.exit_code == 0
        assert "Cache hits: 1" in result.stdout
        assert "Cache misses: 1" in result.stdout


class TestBucketResolution:
    def test_missing_bucket_and_env_var_exits_nonzero(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("S3_BUCKET", raising=False)
        result = runner.invoke(app, ["read", "anything.txt"])
        assert result.exit_code == 1
        assert "S3_BUCKET" in result.output
