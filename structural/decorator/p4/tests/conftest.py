"""Fixtures compartilhadas: ambiente AWS mockado via moto."""

from __future__ import annotations

import os
from collections.abc import Iterator

import boto3
import pytest
from moto import mock_aws

AWS_REGION = "us-east-1"


@pytest.fixture(autouse=True)
def aws_credentials() -> None:
    """Garante credenciais fake para o boto3 não tentar acesso real à AWS."""
    fake_credential_value = "testing"
    os.environ["AWS_ACCESS_KEY_ID"] = fake_credential_value
    os.environ["AWS_SECRET_ACCESS_KEY"] = fake_credential_value
    os.environ["AWS_SECURITY_TOKEN"] = fake_credential_value
    os.environ["AWS_SESSION_TOKEN"] = fake_credential_value
    os.environ["AWS_DEFAULT_REGION"] = AWS_REGION


@pytest.fixture
def moto_aws() -> Iterator[None]:
    """Ativa o mock global da AWS (CloudWatch e Logs) durante o teste."""
    with mock_aws():
        yield


@pytest.fixture
def cloudwatch_logs_client(moto_aws: None) -> boto3.client:
    """Cliente boto3 de CloudWatch Logs apontando para o ambiente mockado."""
    client = boto3.client("logs", region_name=AWS_REGION)
    client.create_log_group(logGroupName="/observability-decorator/traces")
    client.create_log_stream(
        logGroupName="/observability-decorator/traces", logStreamName="default"
    )
    return client
