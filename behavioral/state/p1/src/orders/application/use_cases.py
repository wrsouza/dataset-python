"""Application use cases — orchestrate domain logic.

DIP: use cases depend on the OrderRepository interface, never on concrete infra.
SRP: each use case class has exactly one reason to change.
"""

from __future__ import annotations

from dataclasses import dataclass

from orders.domain.entities import Order, OrderItem
from orders.domain.interfaces import InvalidTransitionError
from orders.infrastructure.repository import OrderRepository


class OrderNotFoundError(Exception):
    def __init__(self, order_id: str) -> None:
        super().__init__(f"Order '{order_id}' not found.")


@dataclass
class CreateOrderRequest:
    items: list[dict[str, object]]  # [{product_id, name, quantity, unit_price}]


class CreateOrderUseCase:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, request: CreateOrderRequest) -> Order:
        order = Order(
            items=[
                OrderItem(
                    product_id=str(i["product_id"]),
                    name=str(i["name"]),
                    quantity=int(str(i["quantity"])),
                    unit_price=float(str(i["unit_price"])),
                )
                for i in request.items
            ]
        )
        self._repository.save(order)
        return order


class TransitionOrderUseCase:
    """Generic use case for any order state transition."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, order_id: str, action: str) -> Order:
        order = self._repository.find_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        action_map = {
            "pay": order.pay,
            "ship": order.ship,
            "deliver": order.deliver,
            "cancel": order.cancel,
            "request_refund": order.request_refund,
            "process_refund": order.process_refund,
        }
        if action not in action_map:
            raise InvalidTransitionError(order.get_current_state_name(), action)

        action_map[action]()
        self._repository.save(order)
        return order
