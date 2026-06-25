"""Shared pytest fixtures for the tax calculation engine test suite."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax.domain.entities import (
    Customer,
    CustomerCountry,
    Order,
    OrderItem,
    OrderType,
)


@pytest.fixture
def order_item() -> OrderItem:
    """A single order item worth 100.00 (qty 2 @ 50.00)."""
    return OrderItem(
        product_id="sku-001",
        description="Wireless mouse",
        quantity=2,
        unit_price=Decimal("50.00"),
    )


@pytest.fixture
def order(order_item: OrderItem) -> Order:
    """A B2C order with a single item, subtotal = 100.00."""
    return Order(
        id="order-1",
        customer_id="customer-1",
        order_type=OrderType.B2C,
        items=[order_item],
    )


@pytest.fixture
def brazilian_customer() -> Customer:
    """A non-exempt customer based in Brazil."""
    return Customer(
        id="customer-1",
        name="Maria Silva",
        country=CustomerCountry.BRAZIL,
        tax_id="123.456.789-00",
    )


@pytest.fixture
def us_customer() -> Customer:
    """A non-exempt customer based in the United States."""
    return Customer(
        id="customer-1",
        name="John Doe",
        country=CustomerCountry.USA,
        tax_id="987-65-4321",
    )


@pytest.fixture
def german_customer() -> Customer:
    """A non-exempt customer based in Germany (EU VAT applies)."""
    return Customer(
        id="customer-1",
        name="Hans Mueller",
        country=CustomerCountry.GERMANY,
        tax_id="DE123456789",
    )


@pytest.fixture
def exempt_customer() -> Customer:
    """A customer with a valid B2B tax-exemption certificate."""
    return Customer(
        id="customer-1",
        name="Acme Corp",
        country=CustomerCountry.OTHER,
        tax_id="EXEMPT-001",
        is_exempt=True,
    )
