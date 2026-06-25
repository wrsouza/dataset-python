from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypeAlias
from uuid import uuid4

OrderId: TypeAlias = str
CustomerId: TypeAlias = str
ProductId: TypeAlias = str


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_FAILED = "payment_failed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REFUNDED = "refunded"


@dataclass
class CartItem:
    product_id: ProductId
    quantity: int
    unit_price: float
    product_name: str

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)


@dataclass
class Customer:
    id: CustomerId
    name: str
    email: str
    address: str


@dataclass
class PaymentMethod:
    card_token: str
    card_last_four: str
    card_brand: str


@dataclass
class StockReservation:
    reservation_id: str
    product_id: ProductId
    quantity: int
    expires_at: datetime


@dataclass
class PaymentCharge:
    charge_id: str
    amount: float
    status: PaymentStatus
    transaction_at: datetime


@dataclass
class ShippingLabel:
    tracking_number: str
    carrier: str
    estimated_days: int
    shipping_cost: float


@dataclass
class Order:
    id: OrderId
    customer_id: CustomerId
    items: list[CartItem]
    total_amount: float
    status: OrderStatus
    payment_charge_id: str | None = None
    tracking_number: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, customer_id: CustomerId, cart: Cart) -> Order:
        return cls(
            id=str(uuid4()),
            customer_id=customer_id,
            items=cart.items,
            total_amount=cart.total,
            status=OrderStatus.PENDING,
        )

    def confirm(self, charge_id: str, tracking_number: str) -> None:
        self.payment_charge_id = charge_id
        self.tracking_number = tracking_number
        self.status = OrderStatus.CONFIRMED
        self.updated_at = datetime.utcnow()

    def mark_payment_failed(self) -> None:
        self.status = OrderStatus.PAYMENT_FAILED
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()


@dataclass
class OrderConfirmation:
    order_id: OrderId
    status: OrderStatus
    total_amount: float
    tracking_number: str
    carrier: str
    estimated_days: int
    message: str
