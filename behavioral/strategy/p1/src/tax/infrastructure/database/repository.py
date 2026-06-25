"""Repository implementations for tax domain entities."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from tax.domain.entities import (
    Customer,
    CustomerCountry,
    Order,
    OrderItem,
    OrderType,
)
from tax.domain.exceptions import CustomerNotFoundError, OrderNotFoundError
from tax.infrastructure.database.models import (
    CustomerModel,
    OrderItemModel,
    OrderModel,
)


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, order_id: str) -> Order:
        model = self._session.get(OrderModel, order_id)
        if model is None:
            raise OrderNotFoundError(order_id)
        return self._to_domain(model)

    def save(self, order: Order) -> None:
        model = OrderModel(
            id=order.id,
            customer_id=order.customer_id,
            order_type=order.order_type.value,
        )
        for item in order.items:
            model.items.append(
                OrderItemModel(
                    product_id=item.product_id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )
        self._session.merge(model)
        self._session.commit()

    @staticmethod
    def _to_domain(model: OrderModel) -> Order:
        items = [
            OrderItem(
                product_id=i.product_id,
                description=i.description,
                quantity=i.quantity,
                unit_price=Decimal(str(i.unit_price)),
            )
            for i in model.items
        ]
        return Order(
            id=model.id,
            customer_id=model.customer_id,
            order_type=OrderType(model.order_type),
            items=items,
        )


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, customer_id: str) -> Customer:
        model = self._session.get(CustomerModel, customer_id)
        if model is None:
            raise CustomerNotFoundError(customer_id)
        return Customer(
            id=model.id,
            name=model.name,
            country=CustomerCountry(model.country),
            tax_id=model.tax_id,
            is_exempt=model.is_exempt,
        )

    def save(self, customer: Customer) -> None:
        model = CustomerModel(
            id=customer.id,
            name=customer.name,
            country=customer.country.value,
            tax_id=customer.tax_id,
            is_exempt=customer.is_exempt,
        )
        self._session.merge(model)
        self._session.commit()
