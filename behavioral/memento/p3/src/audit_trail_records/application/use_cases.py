"""Application use cases for the Model Audit Trail system.

Each use case has a single responsibility and depends only on
abstractions (DIP).
"""

from __future__ import annotations

from dataclasses import dataclass

from audit_trail_records.domain.entities import (
    Product,
    ProductNotFoundError,
    ProductSnapshot,
)
from audit_trail_records.domain.interfaces import AuditTrailCaretaker, ProductRepository


@dataclass
class CreateProductInput:
    product_id: str
    name: str
    price: float
    stock: int
    changed_by: str


@dataclass
class UpdateProductInput:
    product_id: str
    name: str
    price: float
    stock: int
    changed_by: str


class CreateProductUseCase:
    """Creates a new product and saves its initial snapshot.

    SRP: only handles product creation logic.
    DIP: depends on abstractions (repository, caretaker), not concretes.
    """

    def __init__(
        self, repository: ProductRepository, caretaker: AuditTrailCaretaker
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    def execute(self, data: CreateProductInput) -> Product:
        product = Product(
            product_id=data.product_id,
            name=data.name,
            price=data.price,
            stock=data.stock,
            current_version=1,
        )
        product.set_changed_by(data.changed_by)
        snapshot = product.create_snapshot()
        self._repository.save(product)
        self._caretaker.save(product.product_id, snapshot)
        return product


class UpdateProductUseCase:
    """Edits a product, saving a snapshot of the state AFTER the edit.

    OCP: new editing strategies can be injected without modifying this class.
    """

    def __init__(
        self, repository: ProductRepository, caretaker: AuditTrailCaretaker
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    def execute(self, data: UpdateProductInput) -> Product:
        product = self._repository.find_by_id(data.product_id)
        if product is None:
            raise ProductNotFoundError(data.product_id)

        product.set_changed_by(data.changed_by)
        product.apply_edit(data.name, data.price, data.stock)
        snapshot = product.create_snapshot()

        self._repository.save(product)
        self._caretaker.save(product.product_id, snapshot)
        return product


class UndoProductUseCase:
    """Reverts a product to its previous audited snapshot."""

    def __init__(
        self, repository: ProductRepository, caretaker: AuditTrailCaretaker
    ) -> None:
        self._repository = repository
        self._caretaker = caretaker

    def execute(self, product_id: str) -> Product:
        product = self._repository.find_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        snapshot = self._caretaker.undo(product_id)
        product.restore(snapshot)
        self._repository.save(product)
        return product


class GetAuditHistoryUseCase:
    """Returns the full audit trail of a product."""

    def __init__(self, caretaker: AuditTrailCaretaker) -> None:
        self._caretaker = caretaker

    def execute(self, product_id: str) -> list[ProductSnapshot]:
        return self._caretaker.history(product_id)
