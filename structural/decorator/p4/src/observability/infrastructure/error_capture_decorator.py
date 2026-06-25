"""ConcreteDecorator: captura e reporta erros lançados pela operação."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderResult
from observability.domain.interfaces import ErrorReporter, OrderProcessor
from observability.infrastructure.observability_decorator import (
    ObservabilityDecorator,
)


class ErrorCaptureDecorator(ObservabilityDecorator):
    """Reporta exceções da operação decorada antes de relançá-las.

    Nunca silencia o erro (clean_code.md): apenas adiciona observabilidade
    e re-lança a exceção original para o chamador, preservando o contrato
    (Liskov) e mantendo o tratamento de erro do domínio intacto.
    """

    def __init__(self, wrapped: OrderProcessor, reporter: ErrorReporter) -> None:
        super().__init__(wrapped)
        self._reporter = reporter

    def process(self, request: OrderRequest) -> OrderResult:
        """Executa a operação delegada, reportando e relançando erros."""
        try:
            return self._wrapped.process(request)
        except Exception as error:
            self._reporter.report_error(
                operation="process_order",
                error=error,
                attributes={"customer_id": request.customer_id},
            )
            raise
