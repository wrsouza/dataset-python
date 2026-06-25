"""Adapter concreto de TraceExporter usando AWS CloudWatch Logs via boto3."""

from __future__ import annotations

import json
import time
from typing import Any

import boto3

DEFAULT_LOG_GROUP = "/observability-decorator/traces"


class CloudWatchTraceExporter:
    """Exporta spans de tracing como eventos estruturados no CloudWatch Logs."""

    def __init__(
        self,
        region_name: str,
        log_group: str = DEFAULT_LOG_GROUP,
        log_stream: str = "default",
    ) -> None:
        self._client: Any = boto3.client("logs", region_name=region_name)
        self._log_group = log_group
        self._log_stream = log_stream
        self._ensure_log_destination_exists()

    def _ensure_log_destination_exists(self) -> None:
        """Cria log group/stream se ainda não existirem (idempotente)."""
        try:
            self._client.create_log_group(logGroupName=self._log_group)
        except self._client.exceptions.ResourceAlreadyExistsException:
            pass
        try:
            self._client.create_log_stream(
                logGroupName=self._log_group, logStreamName=self._log_stream
            )
        except self._client.exceptions.ResourceAlreadyExistsException:
            pass

    def export_span(
        self, operation: str, duration_ms: float, attributes: dict[str, str]
    ) -> None:
        """Grava um evento de log representando o span da operação."""
        event = {
            "operation": operation,
            "duration_ms": duration_ms,
            "attributes": attributes,
        }
        self._client.put_log_events(
            logGroupName=self._log_group,
            logStreamName=self._log_stream,
            logEvents=[
                {
                    "timestamp": int(time.time() * 1000),
                    "message": json.dumps(event),
                }
            ],
        )
