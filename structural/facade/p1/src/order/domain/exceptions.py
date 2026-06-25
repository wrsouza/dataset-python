from __future__ import annotations


class OrderDomainError(Exception):
    """Base exception for order domain errors."""


class InsufficientStockError(OrderDomainError):
    def __init__(self, product_id: str, requested: int, available: int) -> None:
        self.product_id = product_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for {product_id}: "
            f"requested {requested}, available {available}"
        )


class PaymentDeclinedError(OrderDomainError):
    def __init__(self, reason: str, order_id: str) -> None:
        self.reason = reason
        self.order_id = order_id
        super().__init__(f"Payment declined for order {order_id}: {reason}")


class ShippingError(OrderDomainError):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Shipping error: {reason}")


class OrderNotFoundError(OrderDomainError):
    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")


class OrderPlacementError(OrderDomainError):
    """Raised when the full order placement workflow fails."""

    def __init__(self, reason: str, order_id: str | None = None) -> None:
        self.reason = reason
        self.order_id = order_id
        super().__init__(f"Order placement failed: {reason}")
