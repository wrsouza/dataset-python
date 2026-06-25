from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TypeAlias
from uuid import uuid4

TransactionId: TypeAlias = str
CustomerId: TypeAlias = str


class TransactionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REFUNDED = "refunded"
    FAILED = "failed"


@dataclass
class CreditCard:
    """Raw card data provided by the client before validation."""

    number: str
    exp_month: int
    exp_year: int
    cvc: str
    holder_name: str


@dataclass
class Customer:
    id: CustomerId
    name: str
    email: str


@dataclass
class Charge:
    """Result of a successful Stripe charge."""

    charge_id: str
    amount_cents: int
    currency: str
    created_at: datetime


@dataclass
class Receipt:
    """Confirmation receipt sent to the customer after a successful payment."""

    receipt_id: str
    transaction_id: TransactionId
    sent_to: str
    sent_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Transaction:
    id: TransactionId
    customer_id: CustomerId
    amount_cents: int
    currency: str
    status: TransactionStatus
    charge_id: str | None = None
    failure_reason: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls, customer_id: CustomerId, amount_cents: int, currency: str
    ) -> Transaction:
        return cls(
            id=str(uuid4()),
            customer_id=customer_id,
            amount_cents=amount_cents,
            currency=currency,
            status=TransactionStatus.PENDING,
        )

    def approve(self, charge_id: str) -> None:
        self.charge_id = charge_id
        self.status = TransactionStatus.APPROVED
        self.updated_at = datetime.utcnow()

    def decline(self, reason: str) -> None:
        self.failure_reason = reason
        self.status = TransactionStatus.DECLINED
        self.updated_at = datetime.utcnow()

    def fail(self, reason: str) -> None:
        self.failure_reason = reason
        self.status = TransactionStatus.FAILED
        self.updated_at = datetime.utcnow()

    def refund(self) -> None:
        self.status = TransactionStatus.REFUNDED
        self.updated_at = datetime.utcnow()


@dataclass
class PaymentResult:
    """What the PaymentFacade returns to the caller — a clean DTO."""

    transaction_id: TransactionId
    status: TransactionStatus
    amount_cents: int
    currency: str
    receipt_id: str | None
    message: str
