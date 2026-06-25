"""Configurações lidas de variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_AWS_REGION = "us-east-1"


@dataclass(frozen=True, slots=True)
class Settings:
    """Configuração de runtime da aplicação."""

    aws_region: str
    metrics_namespace: str
    log_group: str

    @staticmethod
    def from_env() -> Settings:
        """Carrega configurações a partir de variáveis de ambiente."""
        return Settings(
            aws_region=os.getenv("AWS_REGION", DEFAULT_AWS_REGION),
            metrics_namespace=os.getenv(
                "CLOUDWATCH_METRICS_NAMESPACE", "ObservabilityDecorator/Orders"
            ),
            log_group=os.getenv(
                "CLOUDWATCH_LOG_GROUP", "/observability-decorator/traces"
            ),
        )
