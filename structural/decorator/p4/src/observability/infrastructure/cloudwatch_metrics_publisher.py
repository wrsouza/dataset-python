"""Adapter concreto de MetricsPublisher usando AWS CloudWatch via boto3."""

from __future__ import annotations

from typing import Any

import boto3

DEFAULT_NAMESPACE = "ObservabilityDecorator/Orders"


class CloudWatchMetricsPublisher:
    """Publica métricas customizadas no AWS CloudWatch."""

    def __init__(self, region_name: str, namespace: str = DEFAULT_NAMESPACE) -> None:
        self._client: Any = boto3.client("cloudwatch", region_name=region_name)
        self._namespace = namespace

    def put_metric(
        self, metric_name: str, value: float, unit: str, dimensions: dict[str, str]
    ) -> None:
        """Envia uma métrica para o CloudWatch sob o namespace configurado."""
        self._client.put_metric_data(
            Namespace=self._namespace,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Dimensions": [
                        {"Name": key, "Value": dim_value}
                        for key, dim_value in dimensions.items()
                    ],
                }
            ],
        )
