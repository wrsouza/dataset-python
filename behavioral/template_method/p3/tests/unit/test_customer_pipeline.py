"""Unit tests for CustomerETLPipeline, against a real (in-memory SQLite) ORM."""

from __future__ import annotations

from typing import Any

import pytest

from etl_pipeline_template.application.pipelines.customer_pipeline import (
    CustomerETLPipeline,
)
from etl_pipeline_template.django_app.models import CustomerModel, CustomerStagingModel

pytestmark = pytest.mark.django_db


def test_run_extracts_transforms_loads_and_publishes(
    fake_kafka_producer: Any,
) -> None:
    CustomerStagingModel.objects.create(
        source_id="c1", full_name="Ana Silva", email="ANA@EXAMPLE.COM"
    )

    result = CustomerETLPipeline().run()

    assert result.pipeline_name == "customer_etl"
    assert result.records_extracted == 1
    assert result.records_loaded == 1

    loaded = CustomerModel.objects.get(source_id="c1")
    assert loaded.first_name == "Ana"
    assert loaded.last_name == "Silva"
    assert loaded.email == "ana@example.com"

    assert len(fake_kafka_producer.sent) == 1


def test_run_with_no_staging_records_loads_nothing() -> None:
    result = CustomerETLPipeline().run()

    assert result.records_extracted == 0
    assert result.records_loaded == 0


def test_run_is_idempotent_for_the_same_source_id() -> None:
    CustomerStagingModel.objects.create(
        source_id="c1", full_name="Ana Silva", email="ana@example.com"
    )
    pipeline = CustomerETLPipeline()

    pipeline.run()
    pipeline.run()

    assert CustomerModel.objects.filter(source_id="c1").count() == 1
