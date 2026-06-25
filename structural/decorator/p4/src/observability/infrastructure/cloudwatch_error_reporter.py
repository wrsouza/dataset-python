"""Adapter concreto de ErrorReporter usando AWS CloudWatch (métrica de erro)."""

from __future__ import annotations

from typing import Any

import boto3

DEFAULT_NAMESPACE = "ObservabilityDecorator/Errors"


class CloudWatchErrorReporter:
    """Publica uma métrica de contagem de erros no AWS CloudWatch."""

    def __init__(self, region_name: str, namespace: str = DEFAULT_NAMESPACE) -> None:
        self._client: Any = boto3.client("cloudwatch", region_name=region_name)
        self._namespace = namespace

    def report_error(
        self, operation: str, error: BaseException, attributes: dict[str, str]
    ) -> None:
        """Envia uma métrica de erro identificando operação e tipo da exceção."""
        dimensions = {
            "Operation": operation,
            "ErrorType": type(error).__name__,
            **attributes,
        }
        self._client.put_metric_data(
            Namespace=self._namespace,
            MetricData=[
                {
                    "MetricName": "ErrorCount",
                    "Value": 1.0,
                    "Unit": "Count",
                    "Dimensions": [
                        {"Name": key, "Value": dim_value}
                        for key, dim_value in dimensions.items()
                    ],
                }
            ],
        )
