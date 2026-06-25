"""Application use cases for the Shopping Cart Visitors system.

Each use case picks the right ConcreteVisitor for the requested
operation, traverses the cart, and persists the resulting report.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from shopping_cart_visitors.application.item_factory import build_items
from shopping_cart_visitors.application.structure import traverse
from shopping_cart_visitors.domain.entities import CartReport, OperationType
from shopping_cart_visitors.domain.exceptions import InvalidOperationError
from shopping_cart_visitors.domain.interfaces import CartVisitor
from shopping_cart_visitors.infrastructure.repository import CartReportRepository
from shopping_cart_visitors.infrastructure.visitors.invoice_formatter import (
    InvoiceFormatterVisitor,
)
from shopping_cart_visitors.infrastructure.visitors.price_calculator import (
    PriceCalculatorVisitor,
)
from shopping_cart_visitors.infrastructure.visitors.shipping_calculator import (
    ShippingCalculatorVisitor,
)

_VISITOR_FACTORIES: dict[OperationType, type[CartVisitor]] = {
    OperationType.PRICE: PriceCalculatorVisitor,
    OperationType.SHIPPING: ShippingCalculatorVisitor,
    OperationType.INVOICE: InvoiceFormatterVisitor,
}


@dataclass
class RunCartOperationInput:
    operation: str
    items: list[dict[str, Any]]


class RunCartOperationUseCase:
    def __init__(self, repository: CartReportRepository) -> None:
        self._repository = repository

    def execute(self, data: RunCartOperationInput) -> CartReport:
        try:
            operation = OperationType(data.operation)
        except ValueError as exc:
            raise InvalidOperationError(data.operation) from exc

        visitor = _VISITOR_FACTORIES[operation]()
        items = build_items(data.items)
        result = traverse(items, visitor)

        report = CartReport(operation=operation, data=result.data)
        self._repository.save(report)
        return report


class GetCartReportsUseCase:
    def __init__(self, repository: CartReportRepository) -> None:
        self._repository = repository

    def execute(self, operation: str) -> list[CartReport]:
        try:
            parsed_operation = OperationType(operation)
        except ValueError as exc:
            raise InvalidOperationError(operation) from exc
        return self._repository.list_for_operation(parsed_operation)
