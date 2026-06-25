"""PostgreSQL repository for orders — infrastructure layer."""

from __future__ import annotations

import json
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from orders.domain.entities import Order, OrderItem, StateTransitionRecord
from orders.domain.interfaces import OrderState
from orders.infrastructure.database import OrderModel, OrderStateHistoryModel
from orders.infrastructure.states import STATE_MAP


class OrderRepository:
    """Persists and rehydrates Order aggregates from PostgreSQL."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, order: Order) -> None:
        row = self._db.get(OrderModel, order.order_id)
        if row is None:
            row = OrderModel(order_id=order.order_id)
            self._db.add(row)

        row.state = order.get_current_state_name()
        row.total = Decimal(str(order.total))
        row.items_json = json.dumps(
            [
                {
                    "product_id": i.product_id,
                    "name": i.name,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                }
                for i in order.items
            ]
        )

        # Persist only unsaved history records (those without a DB row yet)
        existing_count = (
            self._db.query(OrderStateHistoryModel)
            .filter(OrderStateHistoryModel.order_id == order.order_id)
            .count()
        )
        for record in order.history[existing_count:]:
            self._db.add(
                OrderStateHistoryModel(
                    id=str(uuid.uuid4()),
                    order_id=order.order_id,
                    from_state=record.from_state,
                    to_state=record.to_state,
                    action=record.action,
                    occurred_at=record.occurred_at,
                )
            )
        self._db.commit()

    def find_by_id(self, order_id: str) -> Order | None:
        row = self._db.get(OrderModel, order_id)
        if row is None:
            return None
        return self._rehydrate(row)

    def _rehydrate(self, row: OrderModel) -> Order:
        items = [
            OrderItem(
                product_id=i["product_id"],
                name=i["name"],
                quantity=i["quantity"],
                unit_price=i["unit_price"],
            )
            for i in json.loads(row.items_json)
        ]
        history_rows = (
            self._db.query(OrderStateHistoryModel)
            .filter(OrderStateHistoryModel.order_id == row.order_id)
            .order_by(OrderStateHistoryModel.occurred_at)
            .all()
        )
        history = [
            StateTransitionRecord(
                from_state=h.from_state,
                to_state=h.to_state,
                action=h.action,
                occurred_at=h.occurred_at,
            )
            for h in history_rows
        ]

        order = Order.__new__(Order)
        order.order_id = str(row.order_id)
        order.items = items
        order.history = history

        state_cls: type[OrderState] = STATE_MAP[str(row.state)]
        order._state = (
            state_cls()
        )  # noqa: SLF001 — rehydration requires direct assignment
        return order
