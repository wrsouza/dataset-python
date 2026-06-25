"""Integration tests for P1 — Payment Gateway Factory.

Uses SQLite in-memory DB (via conftest) so no external services are needed.
"""
from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from payment.application.use_cases import (
    GetTransactionUseCase,
    ListGatewaysUseCase,
    ProcessPaymentUseCase,
)
from payment.domain.entities import PaymentRequest, PaymentStatus, TransactionNotFoundError
from payment.infrastructure.creators import (
    GATEWAY_REGISTRY,
    StripeGatewayCreator,
)
from payment.infrastructure.repositories import PostgresTransactionRepository


@pytest.fixture
def repository(db_session: Session) -> PostgresTransactionRepository:
    return PostgresTransactionRepository(db_session)


class TestProcessPaymentIntegration:
    def test_stripe_payment_persisted(
        self,
        repository: PostgresTransactionRepository,
        sample_request: PaymentRequest,
    ) -> None:
        use_case = ProcessPaymentUseCase(
            creator=StripeGatewayCreator(), repository=repository
        )
        result = use_case.execute(sample_request)

        assert result.is_successful
        persisted = repository.find_by_id(result.transaction_id)
        assert persisted is not None
        assert persisted.gateway == "Stripe"
        assert persisted.status == PaymentStatus.COMPLETED

    def test_all_gateways_persist_correctly(
        self,
        repository: PostgresTransactionRepository,
        sample_request: PaymentRequest,
    ) -> None:
        for slug, creator in GATEWAY_REGISTRY.items():
            use_case = ProcessPaymentUseCase(creator=creator, repository=repository)
            result = use_case.execute(sample_request)
            assert result.is_successful

        all_txns = repository.list_all()
        assert len(all_txns) == len(GATEWAY_REGISTRY)


class TestGetTransactionIntegration:
    def test_retrieve_existing_transaction(
        self,
        repository: PostgresTransactionRepository,
        sample_request: PaymentRequest,
    ) -> None:
        process = ProcessPaymentUseCase(
            creator=StripeGatewayCreator(), repository=repository
        )
        result = process.execute(sample_request)

        get_use_case = GetTransactionUseCase(repository=repository)
        txn = get_use_case.execute(result.transaction_id)
        assert txn.id == result.transaction_id

    def test_not_found_raises(self, repository: PostgresTransactionRepository) -> None:
        use_case = GetTransactionUseCase(repository=repository)
        with pytest.raises(TransactionNotFoundError):
            use_case.execute("nonexistent_txn")


class TestListGatewaysIntegration:
    def test_lists_all_gateways(self) -> None:
        use_case = ListGatewaysUseCase(registry=GATEWAY_REGISTRY)
        gateways = use_case.execute()
        slugs = {g["slug"] for g in gateways}
        assert slugs == {"stripe", "paypal", "pix"}
