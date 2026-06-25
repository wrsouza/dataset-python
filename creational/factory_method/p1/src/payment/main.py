"""Composition root — wires all dependencies and exposes the FastAPI app."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from payment.domain.entities import (
    PaymentRequest,
    TransactionNotFoundError,
    UnsupportedGatewayError,
)
from payment.application.use_cases import (
    GetTransactionUseCase,
    ListGatewaysUseCase,
    ProcessPaymentUseCase,
)
from payment.infrastructure.creators import GATEWAY_REGISTRY
from payment.infrastructure.database import DATABASE_URL, init_db
from payment.infrastructure.repositories import PostgresTransactionRepository


# ── Engine (shared, created once) ────────────────────────────────────────────

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db(engine)
    yield


app = FastAPI(
    title="Payment Gateway Factory",
    description="Demonstrates Factory Method pattern with multiple payment gateways.",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Dependency helpers ────────────────────────────────────────────────────────

def get_session() -> Session:
    with Session(engine) as session:
        yield session  # type: ignore[misc]


def get_repository(session: Session = Depends(get_session)) -> PostgresTransactionRepository:
    return PostgresTransactionRepository(session)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ProcessPaymentRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount to charge")
    currency: str = Field(min_length=3, max_length=3, description="ISO 4217 currency code")
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaymentResultResponse(BaseModel):
    transaction_id: str
    gateway: str
    status: str
    amount: float
    currency: str
    gateway_reference: str | None = None
    error_message: str | None = None


class TransactionResponse(BaseModel):
    id: str
    gateway: str
    amount: float
    currency: str
    status: str
    created_at: str
    gateway_reference: str | None = None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post(
    "/payments/{gateway}",
    response_model=PaymentResultResponse,
    status_code=201,
    summary="Process a payment via the specified gateway",
)
def process_payment(
    gateway: str = Path(description="Gateway slug: stripe | paypal | pix"),
    body: ProcessPaymentRequest = ...,
    repository: PostgresTransactionRepository = Depends(get_repository),
) -> PaymentResultResponse:
    creator = GATEWAY_REGISTRY.get(gateway)
    if creator is None:
        raise HTTPException(
            status_code=404,
            detail=f"Gateway '{gateway}' not found. Available: {list(GATEWAY_REGISTRY.keys())}",
        )

    use_case = ProcessPaymentUseCase(creator=creator, repository=repository)
    request = PaymentRequest(
        amount=body.amount,
        currency=body.currency.upper(),
        metadata=body.metadata,
    )
    result = use_case.execute(request)

    return PaymentResultResponse(
        transaction_id=result.transaction_id,
        gateway=result.gateway,
        status=result.status.value,
        amount=result.amount,
        currency=result.currency,
        gateway_reference=result.gateway_reference,
        error_message=result.error_message,
    )


@app.get(
    "/payments/{transaction_id}",
    response_model=TransactionResponse,
    summary="Retrieve a transaction by ID",
)
def get_transaction(
    transaction_id: str,
    repository: PostgresTransactionRepository = Depends(get_repository),
) -> TransactionResponse:
    use_case = GetTransactionUseCase(repository=repository)
    try:
        txn = use_case.execute(transaction_id)
    except TransactionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return TransactionResponse(
        id=txn.id,
        gateway=txn.gateway,
        amount=txn.amount,
        currency=txn.currency,
        status=txn.status.value,
        created_at=txn.created_at.isoformat(),
        gateway_reference=txn.gateway_reference,
    )


@app.get(
    "/payments/gateways",
    summary="List all available payment gateways",
)
def list_gateways() -> list[dict[str, str]]:
    use_case = ListGatewaysUseCase(registry=GATEWAY_REGISTRY)
    return use_case.execute()
