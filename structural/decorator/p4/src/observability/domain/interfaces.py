"""Interfaces do pattern Decorator: Component abstrato e métricas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from observability.domain.entities import OrderRequest, OrderResult


class OrderProcessor(ABC):
    """Component: contrato comum a operações de negócio e suas decorações.

    Implementações concretas (ConcreteComponent) executam a regra de negócio.
    Decoradores concretos (ConcreteDecorator) envolvem outro OrderProcessor,
    adicionando comportamento de observabilidade sem alterar esta interface.
    """

    @abstractmethod
    def process(self, request: OrderRequest) -> OrderResult:
        """Processa um pedido e retorna o resultado."""


class MetricsPublisher(Protocol):
    """Abstração para publicação de métricas (ex.: AWS CloudWatch)."""

    def put_metric(
        self, metric_name: str, value: float, unit: str, dimensions: dict[str, str]
    ) -> None:
        """Publica uma métrica numérica com dimensões associadas."""


class TraceExporter(Protocol):
    """Abstração para exportação de spans de rastreamento (tracing)."""

    def export_span(
        self, operation: str, duration_ms: float, attributes: dict[str, str]
    ) -> None:
        """Exporta um span representando a duração de uma operação."""


class ErrorReporter(Protocol):
    """Abstração para captura e reporte de erros."""

    def report_error(
        self, operation: str, error: BaseException, attributes: dict[str, str]
    ) -> None:
        """Reporta um erro capturado durante a execução de uma operação."""
