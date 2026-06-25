"""URL patterns for the etl_pipeline_template app."""

from __future__ import annotations

from django.urls import path

from etl_pipeline_template.django_app.views import (
    run_customer_pipeline,
    run_order_pipeline,
)

app_name = "etl_pipeline_template"

urlpatterns = [
    path("pipelines/customers/run/", run_customer_pipeline, name="run-customers"),
    path("pipelines/orders/run/", run_order_pipeline, name="run-orders"),
]
