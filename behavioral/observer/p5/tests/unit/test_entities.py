"""Unit tests for the MetricEvent domain entity."""

from __future__ import annotations

import pytest

from live_dashboard_observer.domain.entities import MetricEvent


def test_metric_event_rejects_empty_metric_name() -> None:
    with pytest.raises(ValueError, match="metric_name"):
        MetricEvent(metric_name="   ", value=1.0)
