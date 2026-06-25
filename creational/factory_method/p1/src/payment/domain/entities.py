"""Domain entities for the payment domain."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Gateway(str, Enum):
    STRIPE = "stripe"
    PAYPAL = "paypal"
    PIX = "pix"


@dataclass
class PaymentRequest:
    """Value object representing a payment request."""

    amount: float
    currency: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError(f"Amount must be positive, got {self.amount}")
        if len(self.currency) != 3:
            raise ValueError(f"Currency must be ISO 4217 (3 chars), got {self.currency}")


@dataclass
class PaymentResult:
    """Value object representing the result of a payment operation."""

    transaction_id: str
    gateway: str
    status: PaymentStatus
    amount: float
    currency: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    error_message: str | None = None
    gateway_reference: str | None = None

    @property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.COMPLETED


@dataclass
class Transaction:
    """Persisted record of a payment transaction."""

    id: str
    gateway: str
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    gateway_reference: str | None = None
    error_message: str | None = None


class PaymentError(Exception):
    """Base exception for payment domain errors."""

    def __init__(self, reason: str, gateway: str) -> None:
        self.reason = reason
        self.gateway = gateway
        super().__init__(f"Payment error on {gateway}: {reason}")


class TransactionNotFoundError(Exception):
    """Raised when a transaction ID does not exist."""

    def __init__(self, transaction_id: str) -> None:
        self.transaction_id = transaction_id
        super().__init__(f"Transaction not found: {transaction_id}")


class UnsupportedGatewayError(Exception):
    """Raised when an unknown gateway slug is requested."""

    def __init__(self, gateway: str) -> None:
        self.gateway = gateway
        super().__init__(f"Unsupported gateway: {gateway}")
