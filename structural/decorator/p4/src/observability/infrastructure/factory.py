"""Composição (Composition Root) das camadas de decoradores de observabilidade."""

from __future__ import annotations

from observability.application.use_cases import ProcessOrderUseCase
from observability.domain.interfaces import OrderProcessor
from observability.infrastructure.cloudwatch_error_reporter import (
    CloudWatchErrorReporter,
)
from observability.infrastructure.cloudwatch_metrics_publisher import (
    CloudWatchMetricsPublisher,
)
from observability.infrastructure.cloudwatch_trace_exporter import (
    CloudWatchTraceExporter,
)
from observability.infrastructure.error_capture_decorator import (
    ErrorCaptureDecorator,
)
from observability.infrastructure.metrics_decorator import MetricsDecorator
from observability.infrastructure.settings import Settings
from observability.infrastructure.tracing_decorator import TracingDecorator


def build_instrumented_order_processor(settings: Settings) -> OrderProcessor:
    """Monta o ConcreteComponent envolto pelas três camadas de decoradores.

    Ordem de empilhamento (de fora para dentro): ErrorCapture -> Tracing ->
    Metrics -> ProcessOrderUseCase. Erros lançados pelo componente de negócio
    atravessam as camadas internas e são capturados pela camada mais externa.
    """
    base_processor: OrderProcessor = ProcessOrderUseCase()

    metrics_publisher = CloudWatchMetricsPublisher(
        region_name=settings.aws_region, namespace=settings.metrics_namespace
    )
    with_metrics = MetricsDecorator(base_processor, metrics_publisher)

    trace_exporter = CloudWatchTraceExporter(
        region_name=settings.aws_region, log_group=settings.log_group
    )
    with_tracing = TracingDecorator(with_metrics, trace_exporter)

    error_reporter = CloudWatchErrorReporter(
        region_name=settings.aws_region, namespace=settings.metrics_namespace
    )
    return ErrorCaptureDecorator(with_tracing, error_reporter)
