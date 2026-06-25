"""Unit tests for OrderETLPipeline, against a real (in-memory SQLite) ORM."""

from __future__ import annotations

import pytest

from etl_pipeline_template.application.pipelines.order_pipeline import OrderETLPipeline
from etl_pipeline_template.django_app.models import OrderModel, OrderStagingModel

pytestmark = pytest.mark.django_db


def test_run_computes_total_and_loads() -> None:
    OrderStagingModel.objects.create(source_id="o1", unit_price=9.99, quantity=3)

    result = OrderETLPipeline().run()

    assert result.records_loaded == 1
    loaded = OrderModel.objects.get(source_id="o1")
    assert loaded.total == pytest.approx(29.97)


def test_run_with_multiple_staging_records() -> None:
    OrderStagingModel.objects.create(source_id="o1", unit_price=10.0, quantity=2)
    OrderStagingModel.objects.create(source_id="o2", unit_price=5.0, quantity=4)

    result = OrderETLPipeline().run()

    assert result.records_extracted == 2
    assert result.records_loaded == 2
