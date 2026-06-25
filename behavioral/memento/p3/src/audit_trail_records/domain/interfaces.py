"""Domain interfaces for the Model Audit Trail system.

Defines the Memento pattern contracts: Caretaker and the product
repository the Originator state is persisted through.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from audit_trail_records.domain.entities import Product, ProductSnapshot


class ProductRepository(ABC):
    """Persists the current (latest) state of a Product."""

    @abstractmethod
    def save(self, product: Product) -> None:
        """Insert or update a product's current state."""
        ...

    @abstractmethod
    def find_by_id(self, product_id: str) -> Product | None:
        """Return a product by id, or None if it does not exist."""
        ...


class AuditTrailCaretaker(ABC):
    """Caretaker ABC — manages the lifecycle of product snapshots.

    SRP: only stores/retrieves snapshots, has no knowledge of product
    business rules.
    OCP: new storage backends extend this without modifying existing code.
    """

    @abstractmethod
    def save(self, product_id: str, snapshot: ProductSnapshot) -> None:
        """Persist a snapshot for a given product."""
        ...

    @abstractmethod
    def undo(self, product_id: str) -> ProductSnapshot:
        """Return the previous snapshot (one step back)."""
        ...

    @abstractmethod
    def history(self, product_id: str) -> list[ProductSnapshot]:
        """Return all snapshots for a product, ordered oldest to newest."""
        ...
