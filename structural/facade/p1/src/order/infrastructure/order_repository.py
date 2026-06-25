from __future__ import annotations

import json
import logging
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.order.domain.entities import (
    CartItem,
    Order,
    OrderId,
    OrderStatus,
)

logger = logging.getLogger(__name__)


class PostgresOrderRepository:
    """Persists and retrieves orders from PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, order: Order) -> None:
        self._session.execute(
            text(
                "INSERT INTO orders "
                "(id, customer_id, items, total_amount, status, "
                "payment_charge_id, tracking_number, created_at, updated_at) "
                "VALUES "
                "(:id, :cid, :items, :total, :status, :charge, :track, :cat, :uat)"
            ),
            {
                "id": order.id,
                "cid": order.customer_id,
                "items": json.dumps(
                    [
                        {
                            "product_id": i.product_id,
                            "quantity": i.quantity,
                            "unit_price": i.unit_price,
                            "product_name": i.product_name,
                        }
                        for i in order.items
                    ]
                ),
                "total": order.total_amount,
                "status": order.status.value,
                "charge": order.payment_charge_id,
                "track": order.tracking_number,
                "cat": order.created_at,
                "uat": order.updated_at,
            },
        )
        self._session.commit()
        logger.info("Order %s saved", order.id)

    def find_by_id(self, order_id: OrderId) -> Order | None:
        row = self._session.execute(
            text(
                "SELECT id, customer_id, items, total_amount, status, "
                "payment_charge_id, tracking_number, created_at, updated_at "
                "FROM orders WHERE id = :id"
            ),
            {"id": order_id},
        ).fetchone()

        if row is None:
            return None

        items_data = json.loads(row[2])
        return Order(
            id=row[0],
            customer_id=row[1],
            items=[
                CartItem(
                    product_id=i["product_id"],
                    quantity=i["quantity"],
                    unit_price=i["unit_price"],
                    product_name=i["product_name"],
                )
                for i in items_data
            ],
            total_amount=row[3],
            status=OrderStatus(row[4]),
            payment_charge_id=row[5],
            tracking_number=row[6],
            created_at=row[7],
            updated_at=row[8],
        )

    def update(self, order: Order) -> None:
        order.updated_at = datetime.utcnow()
        self._session.execute(
            text(
                "UPDATE orders SET status = :status, "
                "payment_charge_id = :charge, tracking_number = :track, "
                "updated_at = :uat WHERE id = :id"
            ),
            {
                "status": order.status.value,
                "charge": order.payment_charge_id,
                "track": order.tracking_number,
                "uat": order.updated_at,
                "id": order.id,
            },
        )
        self._session.commit()
        logger.info("Order %s updated to status %s", order.id, order.status)
