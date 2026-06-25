"""Unit tests for OrderFacade — all subsystems are mocked."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.order.application.facade import OrderFacade
from src.order.domain.entities import (
    Cart,
    CartItem,
    Customer,
    Order,
    OrderStatus,
    PaymentCharge,
    PaymentMethod,
    PaymentStatus,
    ShippingLabel,
    StockReservation,
)
from src.order.domain.exceptions import (
    InsufficientStockError,
    OrderNotFoundError,
    PaymentDeclinedError,
)


@pytest.fixture
def cart() -> Cart:
    return Cart(
        items=[
            CartItem(
                product_id="PROD001",
                quantity=2,
                unit_price=29.99,
                product_name="Widget Pro",
            )
        ]
    )


@pytest.fixture
def customer() -> Customer:
    return Customer(
        id="CUST001",
        name="Jane Doe",
        email="jane@example.com",
        address="123 Main St",
    )


@pytest.fixture
def payment_method() -> PaymentMethod:
    return PaymentMethod(
        card_token="tok_test_123",
        card_last_four="4242",
        card_brand="Visa",
    )


@pytest.fixture
def mock_reservations() -> list[StockReservation]:
    return [
        StockReservation(
            reservation_id="res_001",
            product_id="PROD001",
            quantity=2,
            expires_at=datetime.utcnow(),
        )
    ]


@pytest.fixture
def mock_charge() -> PaymentCharge:
    return PaymentCharge(
        charge_id="ch_test_001",
        amount=69.97,
        status=PaymentStatus.APPROVED,
        transaction_at=datetime.utcnow(),
    )


@pytest.fixture
def mock_label() -> ShippingLabel:
    return ShippingLabel(
        tracking_number="FS12345678",
        carrier="FastShip",
        estimated_days=3,
        shipping_cost=9.99,
    )


@pytest.fixture
def facade(
    mock_reservations: list[StockReservation],
    mock_charge: PaymentCharge,
    mock_label: ShippingLabel,
) -> OrderFacade:
    inventory = MagicMock()
    inventory.check_availability.return_value = True
    inventory.reserve_stock.return_value = mock_reservations

    payment = MagicMock()
    payment.charge.return_value = mock_charge

    shipping = MagicMock()
    shipping.calculate_shipping.return_value = mock_label
    shipping.generate_label.return_value = mock_label

    notification = MagicMock()
    repository = MagicMock()
    repository.find_by_id.return_value = None

    return OrderFacade(
        inventory=inventory,
        payment=payment,
        shipping=shipping,
        notification=notification,
        repository=repository,
    )


class TestOrderFacadePlaceOrder:
    def test_successful_order_placement(
        self,
        facade: OrderFacade,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
    ) -> None:
        confirmation = facade.place_order(cart, customer, payment_method)

        assert confirmation.order_id is not None
        assert confirmation.status == OrderStatus.CONFIRMED
        assert confirmation.tracking_number == "FS12345678"
        assert confirmation.carrier == "FastShip"
        assert confirmation.estimated_days == 3

    def test_calls_all_subsystems_in_order(
        self,
        facade: OrderFacade,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
    ) -> None:
        facade.place_order(cart, customer, payment_method)

        facade._inventory.check_availability.assert_called_once()
        facade._inventory.reserve_stock.assert_called_once()
        facade._payment.charge.assert_called_once()
        facade._shipping.calculate_shipping.assert_called_once()
        facade._shipping.generate_label.assert_called_once()
        facade._notification.send_order_confirmation.assert_called_once()
        facade._repository.save.assert_called_once()
        facade._repository.update.assert_called_once()

    def test_rolls_back_stock_when_payment_declined(
        self,
        facade: OrderFacade,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
        mock_reservations: list[StockReservation],
    ) -> None:
        facade._payment.charge.side_effect = PaymentDeclinedError(
            reason="Declined", order_id="order_123"
        )

        with pytest.raises(PaymentDeclinedError):
            facade.place_order(cart, customer, payment_method)

        facade._inventory.release_reservation.assert_called_once_with(mock_reservations)
        facade._notification.send_order_failure.assert_called_once()

    def test_raises_insufficient_stock_error(
        self,
        facade: OrderFacade,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
    ) -> None:
        facade._inventory.check_availability.return_value = False

        with pytest.raises(InsufficientStockError):
            facade.place_order(cart, customer, payment_method)

        facade._payment.charge.assert_not_called()
        facade._repository.save.assert_not_called()

    def test_does_not_expose_subsystem_types(
        self,
        facade: OrderFacade,
        cart: Cart,
        customer: Customer,
        payment_method: PaymentMethod,
    ) -> None:
        """The return type is OrderConfirmation — no subsystem leak."""
        from src.order.domain.entities import OrderConfirmation

        result = facade.place_order(cart, customer, payment_method)
        assert isinstance(result, OrderConfirmation)


class TestOrderFacadeGetOrder:
    def test_get_existing_order(self, facade: OrderFacade) -> None:
        order = Order(
            id="order_001",
            customer_id="CUST001",
            items=[],
            total_amount=59.98,
            status=OrderStatus.CONFIRMED,
        )
        facade._repository.find_by_id.return_value = order

        result = facade.get_order("order_001")
        assert result.id == "order_001"

    def test_raises_order_not_found(self, facade: OrderFacade) -> None:
        facade._repository.find_by_id.return_value = None

        with pytest.raises(OrderNotFoundError):
            facade.get_order("nonexistent_id")
