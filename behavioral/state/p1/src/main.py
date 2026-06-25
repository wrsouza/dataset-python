"""FastAPI entry point for the Order State Machine API."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from orders.application.use_cases import (
    CreateOrderRequest,
    CreateOrderUseCase,
    OrderNotFoundError,
    TransitionOrderUseCase,
)
from orders.domain.interfaces import InvalidTransitionError
from orders.infrastructure.database import create_tables, get_db
from orders.infrastructure.repository import OrderRepository


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(title="Order State Machine", version="1.0.0", lifespan=lifespan)


# ── Pydantic schemas ─────────────────────────────────────────────────────────


class ItemIn(BaseModel):
    product_id: str
    name: str
    quantity: int
    unit_price: float


class CreateOrderIn(BaseModel):
    items: list[ItemIn]


class OrderStateOut(BaseModel):
    order_id: str
    state: str
    allowed_transitions: list[str]
    total: float


class HistoryEntryOut(BaseModel):
    from_state: str
    to_state: str
    action: str
    occurred_at: str


# ── Dependency helpers ────────────────────────────────────────────────────────


def get_create_use_case(db: Session = Depends(get_db)) -> CreateOrderUseCase:
    return CreateOrderUseCase(OrderRepository(db))


def get_transition_use_case(db: Session = Depends(get_db)) -> TransitionOrderUseCase:
    return TransitionOrderUseCase(OrderRepository(db))


def get_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.post("/orders", status_code=status.HTTP_201_CREATED, response_model=OrderStateOut)
def create_order(
    body: CreateOrderIn,
    uc: CreateOrderUseCase = Depends(get_create_use_case),
) -> Any:
    order = uc.execute(CreateOrderRequest(items=[i.model_dump() for i in body.items]))
    return OrderStateOut(
        order_id=order.order_id,
        state=order.get_current_state_name(),
        allowed_transitions=order.get_allowed_transitions(),
        total=order.total,
    )


def _transition_route(action: str) -> Any:
    def route(
        order_id: str,
        uc: TransitionOrderUseCase = Depends(get_transition_use_case),
    ) -> Any:
        try:
            order = uc.execute(order_id, action)
        except OrderNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except InvalidTransitionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return OrderStateOut(
            order_id=order.order_id,
            state=order.get_current_state_name(),
            allowed_transitions=order.get_allowed_transitions(),
            total=order.total,
        )

    return route


app.add_api_route(
    "/orders/{order_id}/pay",
    _transition_route("pay"),
    methods=["POST"],
    response_model=OrderStateOut,
)
app.add_api_route(
    "/orders/{order_id}/ship",
    _transition_route("ship"),
    methods=["POST"],
    response_model=OrderStateOut,
)
app.add_api_route(
    "/orders/{order_id}/deliver",
    _transition_route("deliver"),
    methods=["POST"],
    response_model=OrderStateOut,
)
app.add_api_route(
    "/orders/{order_id}/cancel",
    _transition_route("cancel"),
    methods=["POST"],
    response_model=OrderStateOut,
)


@app.get("/orders/{order_id}/state", response_model=OrderStateOut)
def get_order_state(
    order_id: str, repo: OrderRepository = Depends(get_repository)
) -> Any:
    order = repo.find_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return OrderStateOut(
        order_id=order.order_id,
        state=order.get_current_state_name(),
        allowed_transitions=order.get_allowed_transitions(),
        total=order.total,
    )


@app.get("/orders/{order_id}/history", response_model=list[HistoryEntryOut])
def get_order_history(
    order_id: str, repo: OrderRepository = Depends(get_repository)
) -> Any:
    order = repo.find_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return [
        HistoryEntryOut(
            from_state=r.from_state,
            to_state=r.to_state,
            action=r.action,
            occurred_at=r.occurred_at.isoformat(),
        )
        for r in order.history
    ]
