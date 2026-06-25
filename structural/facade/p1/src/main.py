from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from src.order.application.facade import OrderFacade
from src.order.domain.entities import (
    Cart,
    CartItem,
    Customer,
    PaymentMethod,
)
from src.order.domain.exceptions import (
    InsufficientStockError,
    OrderNotFoundError,
    OrderPlacementError,
    PaymentDeclinedError,
)
from src.order.infrastructure.database import create_tables, get_session, init_engine
from src.order.infrastructure.inventory_service import PostgresInventoryService
from src.order.infrastructure.notification_service import SQSNotificationService
from src.order.infrastructure.order_repository import PostgresOrderRepository
from src.order.infrastructure.payment_service import MockPaymentService
from src.order.infrastructure.shipping_service import MockShippingService


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    database_url = os.getenv("DATABASE_URL", "postgresql://app:secret@db:5432/appdb")
    init_engine(database_url)
    create_tables(database_url)
    yield


app = FastAPI(
    title="E-commerce Order Facade",
    description="Demonstrates the Facade pattern for order placement",
    version="1.0.0",
    lifespan=lifespan,
)


def build_facade() -> OrderFacade:
    """Composition root — assembles the Facade with all subsystem dependencies."""
    session = get_session()
    queue_url = os.getenv("SQS_QUEUE_URL", "http://localstack:4566/000000000000/orders")
    # An explicitly empty AWS_ENDPOINT_URL ("") means "use the real AWS
    # endpoint" (e.g. when moto intercepts boto3 calls in tests); only fall
    # back to LocalStack when the variable is entirely unset.
    localstack_url = (
        os.environ.get("AWS_ENDPOINT_URL", "http://localstack:4566") or None
    )

    return OrderFacade(
        inventory=PostgresInventoryService(session),
        payment=MockPaymentService(),
        shipping=MockShippingService(),
        notification=SQSNotificationService(queue_url, localstack_url),
        repository=PostgresOrderRepository(session),
    )


# ── Request / Response schemas ─────────────────────────────────────────────────


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    product_name: str


class PlaceOrderRequest(BaseModel):
    customer_id: str
    customer_name: str
    customer_email: str
    customer_address: str
    items: list[CartItemRequest]
    card_token: str
    card_last_four: str
    card_brand: str


class OrderResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    tracking_number: str
    carrier: str
    estimated_days: int
    message: str


class OrderDetailResponse(BaseModel):
    order_id: str
    customer_id: str
    status: str
    total_amount: float
    payment_charge_id: str | None
    tracking_number: str | None


# ── Routes ────────────────────────────────────────────────────────────────────


@app.post("/orders", response_model=OrderResponse, status_code=201)
def place_order(
    request: PlaceOrderRequest,
    facade: OrderFacade = Depends(build_facade),
) -> OrderResponse:
    """
    Place a new order.

    This single endpoint calls the OrderFacade — no subsystem is exposed
    to the HTTP layer. The client only deals with a clean domain contract.
    """
    cart = Cart(
        items=[
            CartItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product_name=item.product_name,
            )
            for item in request.items
        ]
    )
    customer = Customer(
        id=request.customer_id,
        name=request.customer_name,
        email=request.customer_email,
        address=request.customer_address,
    )
    payment_method = PaymentMethod(
        card_token=request.card_token,
        card_last_four=request.card_last_four,
        card_brand=request.card_brand,
    )

    try:
        confirmation = facade.place_order(cart, customer, payment_method)
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PaymentDeclinedError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    except OrderPlacementError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OrderResponse(
        order_id=confirmation.order_id,
        status=confirmation.status.value,
        total_amount=confirmation.total_amount,
        tracking_number=confirmation.tracking_number,
        carrier=confirmation.carrier,
        estimated_days=confirmation.estimated_days,
        message=confirmation.message,
    )


@app.get("/orders/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    facade: OrderFacade = Depends(build_facade),
) -> OrderDetailResponse:
    """Retrieve order details by ID."""
    try:
        order = facade.get_order(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return OrderDetailResponse(
        order_id=order.id,
        customer_id=order.customer_id,
        status=order.status.value,
        total_amount=order.total_amount,
        payment_charge_id=order.payment_charge_id,
        tracking_number=order.tracking_number,
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
