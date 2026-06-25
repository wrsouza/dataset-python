"""Domain entities for the Model Audit Trail system."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ProductSnapshot:
    """Immutable snapshot of a product's state at a point in time.

    frozen=True enforces the Memento pattern guarantee: once captured,
    a snapshot cannot be mutated — only read or discarded.
    """

    name: str
    price: float
    stock: int
    version: int
    changed_by: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version}")
        if not self.changed_by.strip():
            raise ValueError("changed_by cannot be empty")


@dataclass
class Product:
    """Originator — holds current product state and produces/restores snapshots.

    SRP: Product only manages its own field state.
    It does not persist itself — that is the repository's job.
    """

    product_id: str
    name: str
    price: float
    stock: int
    current_version: int = 1
    _changed_by: str = field(default="system", repr=False)

    def set_changed_by(self, changed_by: str) -> None:
        """Set who is responsible for the next snapshot."""
        self._changed_by = changed_by

    def create_snapshot(self) -> ProductSnapshot:
        """Capture current state into an immutable ProductSnapshot."""
        return ProductSnapshot(
            name=self.name,
            price=self.price,
            stock=self.stock,
            version=self.current_version,
            changed_by=self._changed_by,
        )

    def restore(self, snapshot: ProductSnapshot) -> None:
        """Restore product state from a previously captured snapshot.

        The Product does not know how the snapshot was stored — that is
        the Caretaker's concern (Separation of Concerns / SRP).
        """
        self.name = snapshot.name
        self.price = snapshot.price
        self.stock = snapshot.stock
        self.current_version = snapshot.version

    def apply_edit(self, name: str, price: float, stock: int) -> None:
        """Apply new field values, incrementing the version counter."""
        self.name = name
        self.price = price
        self.stock = stock
        self.current_version += 1


class ProductNotFoundError(Exception):
    """Raised when a product does not exist in the repository."""

    def __init__(self, product_id: str) -> None:
        super().__init__(f"Product '{product_id}' not found")
        self.product_id = product_id


class NoHistoryError(Exception):
    """Raised when undo is requested but no previous snapshot exists."""

    def __init__(self, product_id: str) -> None:
        super().__init__(f"No audit history available for product '{product_id}'")
        self.product_id = product_id
