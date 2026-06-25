"""Testes unitários do CloudWatchTraceExporter com moto."""

from __future__ import annotations

import boto3

from observability.infrastructure.cloudwatch_trace_exporter import (
    CloudWatchTraceExporter,
)


def test_export_span_writes_log_event(cloudwatch_logs_client: boto3.client) -> None:
    exporter = CloudWatchTraceExporter(region_name="us-east-1")

    exporter.export_span(
        operation="process_order",
        duration_ms=15.2,
        attributes={"customer_id": "c1"},
    )

    response = cloudwatch_logs_client.get_log_events(
        logGroupName="/observability-decorator/traces", logStreamName="default"
    )
    assert len(response["events"]) == 1
    assert "process_order" in response["events"][0]["message"]
