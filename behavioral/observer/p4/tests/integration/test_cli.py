"""Integration tests for the Typer CLI, using moto to fake AWS SNS."""

from __future__ import annotations

from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws
from typer.testing import CliRunner

from cloud_event_notifier.main import app

runner = CliRunner()


@pytest.fixture
def env() -> Iterator[dict[str, str]]:
    with mock_aws():
        client = boto3.client("sns", region_name="us-east-1")
        topic_arn = client.create_topic(Name="cloud-events")["TopicArn"]
        yield {"AWS_REGION": "us-east-1", "SNS_TOPIC_ARN": topic_arn}


def test_publish_echoes_confirmation(env: dict[str, str]) -> None:
    # Typer flattens a single-command app: with only one command
    # registered ("publish"), the command name itself is not part of
    # the CLI invocation — only its arguments are.
    result = runner.invoke(app, ["order.created", '{"order_id": "o1"}'], env=env)

    assert result.exit_code == 0
    assert "order.created" in result.stdout
    assert "order_id" in result.stdout
    assert "Published" in result.stdout
