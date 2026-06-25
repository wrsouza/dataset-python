"""Caso de uso: ConcreteComponent do pattern Decorator."""

from __future__ import annotations

from observability.domain.entities import OrderRequest, OrderResult
from observability.domain.exceptions import InvalidOrderError
from observability.domain.interfaces import OrderProcessor

MAX_QUANTITY_PER_ORDER = 1000


class ProcessOrderUseCase(OrderProcessor):
    """ConcreteComponent: lógica de negócio pura de processamento de pedidos.

    Não conhece métricas, tracing ou captura de erros — essas
    responsabilidades são adicionadas por decoradores em infrastructure/.
    """

    def process(self, request: OrderRequest) -> OrderResult:
        """Valida e processa um pedido, retornando o resultado calculado."""
        self._validate(request)
        return OrderResult.new_processed(total_amount=request.total_amount())

    def _validate(self, request: OrderRequest) -> None:
        if request.quantity <= 0:
            raise InvalidOrderError("quantity must be positive")
        if request.quantity > MAX_QUANTITY_PER_ORDER:
            raise InvalidOrderError(
                f"quantity exceeds limit of {MAX_QUANTITY_PER_ORDER}"
            )
        if request.unit_price <= 0:
            raise InvalidOrderError("unit_price must be positive")
