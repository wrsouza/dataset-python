from __future__ import annotations

from typing import Protocol

from src.order.domain.entities import (
    Cart,
    CartItem,
    Customer,
    Order,
    OrderId,
    PaymentCharge,
    PaymentMethod,
    ShippingLabel,
    StockReservation,
)


class InventoryServiceProtocol(Protocol):
    """Checks and reserves product inventory."""

    def check_availability(self, items: list[CartItem]) -> bool: ...

    def reserve_stock(self, items: list[CartItem]) -> list[StockReservation]: ...

    def release_reservation(self, reservations: list[StockReservation]) -> None: ...


class PaymentServiceProtocol(Protocol):
    """Processes payment charges and refunds."""

    def charge(
        self,
        amount: float,
        payment_method: PaymentMethod,
        order_id: OrderId,
    ) -> PaymentCharge: ...

    def refund(self, charge_id: str) -> bool: ...


class ShippingServiceProtocol(Protocol):
    """Calculates shipping cost and generates labels."""

    def calculate_shipping(self, customer: Customer, cart: Cart) -> ShippingLabel: ...

    def generate_label(self, order: Order, label: ShippingLabel) -> ShippingLabel: ...


class NotificationServiceProtocol(Protocol):
    """Sends order notifications via messaging queue."""

    def send_order_confirmation(
        self,
        order: Order,
        customer: Customer,
        label: ShippingLabel,
    ) -> None: ...

    def send_order_failure(self, order: Order, customer: Customer) -> None: ...


class OrderRepositoryProtocol(Protocol):
    """Persists and retrieves orders."""

    def save(self, order: Order) -> None: ...

    def find_by_id(self, order_id: OrderId) -> Order | None: ...

    def update(self, order: Order) -> None: ...
