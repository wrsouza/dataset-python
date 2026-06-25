"""Testes unitários do CloudWatchMetricsPublisher com moto."""

from __future__ import annotations

from observability.infrastructure.cloudwatch_metrics_publisher import (
    CloudWatchMetricsPublisher,
)


def test_put_metric_sends_data_to_cloudwatch(moto_aws: None) -> None:
    publisher = CloudWatchMetricsPublisher(region_name="us-east-1")

    publisher.put_metric(
        metric_name="ProcessOrderDuration",
        value=12.5,
        unit="Milliseconds",
        dimensions={"Operation": "process_order"},
    )

    response = publisher._client.list_metrics(Namespace="ObservabilityDecorator/Orders")
    metric_names = [m["MetricName"] for m in response["Metrics"]]
    assert "ProcessOrderDuration" in metric_names
