"""FastAPI application for the Cursor Pagination / Order Export service.

Composition root: the only place that wires the concrete PostgreSQL
repository into the use cases.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.responses import StreamingResponse

from order_pagination.application.use_cases import (
    ExportAllOrdersUseCase,
    ListOrdersPageUseCase,
)
from order_pagination.domain.entities import Order
from order_pagination.domain.interfaces import OrderRepository
from order_pagination.infrastructure.factory import build_repository

app = FastAPI(
    title="Order Pagination — Iterator Pattern",
    description=(
        "Iterator pattern: CursorOrderIterator traverses the full order "
        "collection lazily, fetching pages from PostgreSQL on demand."
    ),
    version="1.0.0",
)

_repository: OrderRepository | None = None


def get_repository() -> OrderRepository:
    global _repository
    if _repository is None:
        _repository = build_repository()
    return _repository


def _order_to_dict(order: Order) -> dict[str, object]:
    return {
        "order_id": order.order_id,
        "customer": order.customer,
        "amount": order.amount,
        "created_at": order.created_at.isoformat(),
    }


@app.get("/orders")
def list_orders(
    repository: Annotated[OrderRepository, Depends(get_repository)],
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
) -> dict[str, object]:
    """Return a single page of orders, following typical cursor pagination."""
    use_case = ListOrdersPageUseCase(repository)
    page = use_case.execute(cursor, limit)
    return {
        "items": [_order_to_dict(order) for order in page.items],
        "next_cursor": page.next_cursor,
    }


@app.get("/orders/export")
def export_orders(
    repository: Annotated[OrderRepository, Depends(get_repository)],
) -> StreamingResponse:
    """Stream every order as newline-delimited JSON via the GoF Iterator."""
    use_case = ExportAllOrdersUseCase(repository)

    def _stream() -> Iterator[str]:
        for order in use_case.execute():
            yield json.dumps(_order_to_dict(order)) + "\n"

    return StreamingResponse(_stream(), media_type="application/x-ndjson")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
