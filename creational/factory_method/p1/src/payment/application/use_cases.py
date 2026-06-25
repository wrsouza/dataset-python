"""Application use cases — depend on abstractions only (DIP).

Use cases interact with PaymentGatewayCreator and TransactionRepository
without knowing which concrete implementation is injected.
"""
from __future__ import annotations

import uuid

from payment.domain.entities import (
    Gateway,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    Transaction,
    TransactionNotFoundError,
    UnsupportedGatewayError,
)
from payment.domain.interfaces import PaymentGatewayCreator
from payment.domain.repositories import TransactionRepository


class ProcessPaymentUseCase:
    """Orchestrates a payment through whichever gateway creator is injected.

    Depends on PaymentGatewayCreator (abstraction) — never on a concrete
    gateway class.  The correct creator is selected by the registry and
    injected by the composition root (main.py).
    """

    def __init__(
        self,
        creator: PaymentGatewayCreator,
        repository: TransactionRepository,
    ) -> None:
        self._creator = creator
        self._repository = repository

    def execute(self, request: PaymentRequest) -> PaymentResult:
        """Process the payment and persist the transaction record."""
        processor = self._creator.create_payment_processor()
        result = processor.process(request)

        transaction = Transaction(
            id=result.transaction_id,
            gateway=self._creator.get_gateway_name(),
            amount=result.amount,
            currency=result.currency,
            status=result.status,
            created_at=result.created_at,
            gateway_reference=result.gateway_reference,
            error_message=result.error_message,
        )
        self._repository.save(transaction)
        return result


class GetTransactionUseCase:
    """Retrieve a single transaction by its ID."""

    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def execute(self, transaction_id: str) -> Transaction:
        transaction = self._repository.find_by_id(transaction_id)
        if transaction is None:
            raise TransactionNotFoundError(transaction_id)
        return transaction


class ListGatewaysUseCase:
    """Return metadata about all registered gateways."""

    def __init__(self, registry: dict[str, PaymentGatewayCreator]) -> None:
        self._registry = registry

    def execute(self) -> list[dict[str, str]]:
        return [
            {"slug": slug, "name": creator.get_gateway_name()}
            for slug, creator in self._registry.items()
        ]
