"""Testes unitários de Settings.from_env."""

from __future__ import annotations

import pytest

from observability.infrastructure.settings import Settings


def test_from_env_uses_defaults_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("CLOUDWATCH_METRICS_NAMESPACE", raising=False)
    monkeypatch.delenv("CLOUDWATCH_LOG_GROUP", raising=False)

    settings = Settings.from_env()

    assert settings.aws_region == "us-east-1"
    assert settings.metrics_namespace == "ObservabilityDecorator/Orders"
    assert settings.log_group == "/observability-decorator/traces"


def test_from_env_reads_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("CLOUDWATCH_METRICS_NAMESPACE", "Custom/Namespace")
    monkeypatch.setenv("CLOUDWATCH_LOG_GROUP", "/custom/log-group")

    settings = Settings.from_env()

    assert settings.aws_region == "eu-west-1"
    assert settings.metrics_namespace == "Custom/Namespace"
    assert settings.log_group == "/custom/log-group"
