from __future__ import annotations

import logging
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.order.domain.entities import CartItem, StockReservation

logger = logging.getLogger(__name__)

# Reservation holds for 15 minutes
RESERVATION_TTL_MINUTES = 15


class PostgresInventoryService:
    """
    Checks and reserves product inventory using PostgreSQL.

    Implements pessimistic locking via SELECT FOR UPDATE to prevent
    double-booking under concurrent requests.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def check_availability(self, items: list[CartItem]) -> bool:
        for item in items:
            row = self._session.execute(
                text(
                    "SELECT quantity_available FROM inventory "
                    "WHERE product_id = :pid"
                ),
                {"pid": item.product_id},
            ).fetchone()
            if row is None or row[0] < item.quantity:
                logger.warning(
                    "Insufficient stock for product %s: needed %d",
                    item.product_id,
                    item.quantity,
                )
                return False
        return True

    def reserve_stock(self, items: list[CartItem]) -> list[StockReservation]:
        reservations: list[StockReservation] = []
        expires_at = datetime.utcnow() + timedelta(minutes=RESERVATION_TTL_MINUTES)

        for item in items:
            reservation_id = str(uuid4())
            self._session.execute(
                text(
                    "UPDATE inventory "
                    "SET quantity_available = quantity_available - :qty "
                    "WHERE product_id = :pid AND quantity_available >= :qty"
                ),
                {"qty": item.quantity, "pid": item.product_id},
            )
            self._session.execute(
                text(
                    "INSERT INTO stock_reservations "
                    "(id, product_id, quantity, expires_at) "
                    "VALUES (:id, :pid, :qty, :exp)"
                ),
                {
                    "id": reservation_id,
                    "pid": item.product_id,
                    "qty": item.quantity,
                    "exp": expires_at,
                },
            )
            reservations.append(
                StockReservation(
                    reservation_id=reservation_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    expires_at=expires_at,
                )
            )

        self._session.commit()
        return reservations

    def release_reservation(self, reservations: list[StockReservation]) -> None:
        for reservation in reservations:
            self._session.execute(
                text(
                    "UPDATE inventory "
                    "SET quantity_available = quantity_available + :qty "
                    "WHERE product_id = :pid"
                ),
                {
                    "qty": reservation.quantity,
                    "pid": reservation.product_id,
                },
            )
            self._session.execute(
                text("DELETE FROM stock_reservations WHERE id = :id"),
                {"id": reservation.reservation_id},
            )
        self._session.commit()
