"""FastAPI application entrypoint for Tax Calculation Engine."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from tax.application.context import TaxCalculator
from tax.domain.entities import (
    Order,
    OrderItem,
    OrderType,
)
from tax.domain.exceptions import (
    CustomerNotFoundError,
    InvalidStrategyError,
    OrderNotFoundError,
)
from tax.infrastructure.database.connection import engine, get_db
from tax.infrastructure.database.models import Base
from tax.infrastructure.database.repository import CustomerRepository, OrderRepository
from tax.infrastructure.strategies.registry import get_all_strategies, get_strategy

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tax Calculation Engine",
    description="Strategy pattern: tax calculation for multiple jurisdictions",
    version="1.0.0",
)


# ── Pydantic schemas ─────────────────────────────────────────────────────────


class OrderItemIn(BaseModel):
    product_id: str
    description: str
    quantity: int
    unit_price: Decimal


class OrderIn(BaseModel):
    customer_id: str
    order_type: OrderType
    items: list[OrderItemIn]


class TaxLineOut(BaseModel):
    name: str
    rate: Decimal
    amount: Decimal
    description: str


class TaxBreakdownOut(BaseModel):
    subtotal: Decimal
    taxes: list[TaxLineOut]
    total: Decimal
    effective_rate: Decimal
    strategy_used: str


class StrategyInfo(BaseModel):
    name: str
    description: str


# ── Routes ───────────────────────────────────────────────────────────────────


@app.get("/tax/strategies", response_model=list[StrategyInfo])
def list_strategies() -> list[StrategyInfo]:
    """List all available tax strategies."""
    return [
        StrategyInfo(name=s.get_name(), description=s.get_description())
        for s in get_all_strategies().values()
    ]


@app.post("/orders", status_code=201)
def create_order(
    payload: OrderIn,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Persist a new order."""
    order = Order(
        id=str(uuid.uuid4()),
        customer_id=payload.customer_id,
        order_type=payload.order_type,
        items=[
            OrderItem(
                product_id=i.product_id,
                description=i.description,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in payload.items
        ],
    )
    OrderRepository(db).save(order)
    return {"id": order.id, "status": "created"}


@app.post("/orders/{order_id}/calculate-tax", response_model=TaxBreakdownOut)
def calculate_tax(
    order_id: str,
    db: Annotated[Session, Depends(get_db)],
    strategy: Annotated[str, Query(description="brazil|us|eu|exempt")] = "brazil",
) -> TaxBreakdownOut:
    """Calculate taxes for an order using the specified strategy."""
    try:
        order_repo = OrderRepository(db)
        customer_repo = CustomerRepository(db)

        order = order_repo.find_by_id(order_id)
        customer = customer_repo.find_by_id(order.customer_id)
        tax_strategy = get_strategy(strategy)

        calculator = TaxCalculator(strategy=tax_strategy)
        breakdown = calculator.calculate(order, customer)

        return TaxBreakdownOut(
            subtotal=breakdown.subtotal,
            taxes=[
                TaxLineOut(
                    name=t.name,
                    rate=t.rate,
                    amount=t.amount,
                    description=t.description,
                )
                for t in breakdown.taxes
            ],
            total=breakdown.total,
            effective_rate=breakdown.effective_rate,
            strategy_used=breakdown.strategy_used,
        )
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidStrategyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
