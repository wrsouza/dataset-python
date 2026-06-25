"""Base Decorator abstrato — empacota um OrderProcessor para extensão."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderResult
from observability.domain.interfaces import OrderProcessor


class ObservabilityDecorator(OrderProcessor):
    """Decorator base: mantém referência ao componente decorado.

    Subclasses (MetricsDecorator, TracingDecorator, ErrorCaptureDecorator)
    sobrescrevem `process` para adicionar comportamento antes/depois de
    delegar ao componente envolvido, mantendo a mesma interface OrderProcessor
    (Liskov) e permitindo empilhamento livre (Open/Closed).
    """

    def __init__(self, wrapped: OrderProcessor) -> None:
        self._wrapped = wrapped

    def process(self, request: OrderRequest) -> OrderResult:
        """Delega diretamente ao componente decorado (comportamento padrão)."""
        return self._wrapped.process(request)
