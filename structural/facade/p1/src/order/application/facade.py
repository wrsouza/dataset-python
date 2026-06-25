"""
OrderFacade — single entry point for the complete order placement workflow.

Hides the complexity of inventory, payment, shipping, notification and
persistence subsystems. The client (HTTP route) calls only this class.
"""

from __future__ import annotations

import logging

from src.order.domain.entities import (
    Cart,
    Customer,
    Order,
    OrderConfirmation,
    OrderId,
    PaymentMethod,
    StockReservation,
)
from src.order.domain.exceptions import (
    InsufficientStockError,
    OrderNotFoundError,
    OrderPlacementError,
    PaymentDeclinedError,
)
from src.order.domain.interfaces import (
    InventoryServiceProtocol,
    NotificationServiceProtocol,
    OrderRepositoryProtocol,
    PaymentServiceProtocol,
    ShippingServiceProtocol,
)

logger = logging.getLogger(__name__)


class OrderFacade:
    """
    Facade that orchestrates all subsystems to place an order.

    Client code only depends on this class — not on any subsystem.
    Provides automatic rollback if any step fails after partial completion.
    """

    def __init__(
        self,
        inventory: InventoryServiceProtocol,
        payment: PaymentServiceProtocol,
        shipping: ShippingServiceProtocol,
        notification: NotificationServiceProtocol,
        repository: OrderRepositoryProtocol,
    ) -> None:
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notification = notification
        self._repository = repository

    def place_order(
        self,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
    ) -> OrderConfirmation:
        """
        Execute the full order placement workflow.

        Steps (with rollback on failure):
          1. Check inventory availability
          2. Reserve stock
          3. Calculate shipping
          4. Create and persist the order
          5. Process payment
          6. Generate shipping label
          7. Confirm order and persist final state
          8. Send confirmation notification
        """
        reservations: list[StockReservation] = []
        order: Order | None = None

        try:
            self._ensure_stock_available(cart)
            reservations = self._inventory.reserve_stock(cart.items)
            logger.info("Stock reserved for customer %s", customer.id)

            shipping_label = self._shipping.calculate_shipping(customer, cart)

            order = Order.create(customer.id, cart)
            self._repository.save(order)
            logger.info("Order %s created", order.id)

            charge = self._payment.charge(
                cart.total + shipping_label.shipping_cost,
                payment_method,
                order.id,
            )

            final_label = self._shipping.generate_label(order, shipping_label)
            order.confirm(charge.charge_id, final_label.tracking_number)
            self._repository.update(order)

            self._notification.send_order_confirmation(order, customer, final_label)
            logger.info(
                "Order %s confirmed, tracking %s", order.id, final_label.tracking_number
            )

            confirmation_message = (
                f"Order confirmed! Your package will arrive in "
                f"{final_label.estimated_days} business days."
            )
            return OrderConfirmation(
                order_id=order.id,
                status=order.status,
                total_amount=order.total_amount,
                tracking_number=final_label.tracking_number,
                carrier=final_label.carrier,
                estimated_days=final_label.estimated_days,
                message=confirmation_message,
            )

        except InsufficientStockError:
            self._rollback_reservations(reservations)
            raise

        except PaymentDeclinedError:
            self._rollback_reservations(reservations)
            if order is not None:
                order.mark_payment_failed()
                self._repository.update(order)
                self._notification.send_order_failure(order, customer)
            raise

        except Exception as exc:
            logger.error("Unexpected error placing order: %s", exc)
            self._rollback_reservations(reservations)
            if order is not None:
                order.cancel()
                self._repository.update(order)
            raise OrderPlacementError(str(exc), order.id if order else None) from exc

    def get_order(self, order_id: OrderId) -> Order:
        """Retrieve an order by ID."""
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def _ensure_stock_available(self, cart: Cart) -> None:
        if not self._inventory.check_availability(cart.items):
            raise InsufficientStockError(
                product_id="multiple",
                requested=0,
                available=0,
            )

    def _rollback_reservations(self, reservations: list[StockReservation]) -> None:
        if reservations:
            try:
                self._inventory.release_reservation(reservations)
                logger.info("Stock reservations rolled back")
            except Exception as exc:
                # Log and continue — rollback failures should not mask original errors
                logger.error("Failed to release stock reservations: %s", exc)
