"""HTTP views exposing the ETL Pipeline Template: trigger each pipeline."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from etl_pipeline_template.application.pipelines.customer_pipeline import (
    CustomerETLPipeline,
)
from etl_pipeline_template.application.pipelines.order_pipeline import OrderETLPipeline
from etl_pipeline_template.domain.entities import ETLResult


def _result_to_dict(result: ETLResult) -> dict[str, object]:
    return {
        "pipeline_name": result.pipeline_name,
        "records_extracted": result.records_extracted,
        "records_loaded": result.records_loaded,
        "occurred_at": result.occurred_at.isoformat(),
    }


@csrf_exempt
@require_http_methods(["POST"])
def run_customer_pipeline(request: HttpRequest) -> JsonResponse:
    """POST /pipelines/customers/run/"""
    result = CustomerETLPipeline().run()
    return JsonResponse(_result_to_dict(result), status=201)


@csrf_exempt
@require_http_methods(["POST"])
def run_order_pipeline(request: HttpRequest) -> JsonResponse:
    """POST /pipelines/orders/run/"""
    result = OrderETLPipeline().run()
    return JsonResponse(_result_to_dict(result), status=201)
