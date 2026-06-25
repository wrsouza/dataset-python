"""Integration tests for the etl_pipeline_template Django views."""

from __future__ import annotations

import pytest
from django.test import Client

from etl_pipeline_template.django_app.models import (
    CustomerStagingModel,
    OrderStagingModel,
)

pytestmark = pytest.mark.django_db


def test_run_customer_pipeline_returns_201(client: Client) -> None:
    CustomerStagingModel.objects.create(
        source_id="c1", full_name="Ana Silva", email="ana@example.com"
    )

    response = client.post("/pipelines/customers/run/")

    body = response.json()
    assert response.status_code == 201
    assert body["pipeline_name"] == "customer_etl"
    assert body["records_loaded"] == 1


def test_run_order_pipeline_returns_201(client: Client) -> None:
    OrderStagingModel.objects.create(source_id="o1", unit_price=10.0, quantity=2)

    response = client.post("/pipelines/orders/run/")

    body = response.json()
    assert response.status_code == 201
    assert body["pipeline_name"] == "order_etl"
    assert body["records_loaded"] == 1
