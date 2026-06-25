"""Testes unitários do CloudWatchErrorReporter com moto."""

from __future__ import annotations

from observability.infrastructure.cloudwatch_error_reporter import (
    CloudWatchErrorReporter,
)


def test_report_error_publishes_error_count_metric(moto_aws: None) -> None:
    reporter = CloudWatchErrorReporter(region_name="us-east-1")

    reporter.report_error(
        operation="process_order",
        error=ValueError("boom"),
        attributes={"customer_id": "c1"},
    )

    response = reporter._client.list_metrics(Namespace="ObservabilityDecorator/Errors")
    metric_names = [m["MetricName"] for m in response["Metrics"]]
    assert "ErrorCount" in metric_names
