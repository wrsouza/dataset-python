"""Repository abstractions for the payment domain (DIP)."""
from __future__ import annotations

from typing import Protocol

from payment.domain.entities import Transaction


class TransactionRepository(Protocol):
    """Persistence interface — use cases depend on this, not on concrete DB."""

    def save(self, transaction: Transaction) -> None:
        """Persist a transaction record."""
        ...

    def find_by_id(self, transaction_id: str) -> Transaction | None:
        """Retrieve a transaction by its ID. Returns None if not found."""
        ...

    def list_all(self) -> list[Transaction]:
        """Return all transactions ordered by creation date descending."""
        ...
