"""Unit tests for Model Audit Trail use cases, against in-memory fakes."""

from __future__ import annotations

import pytest

from audit_trail_records.application.use_cases import (
    CreateProductInput,
    CreateProductUseCase,
    GetAuditHistoryUseCase,
    UndoProductUseCase,
    UpdateProductInput,
    UpdateProductUseCase,
)
from audit_trail_records.domain.entities import (
    NoHistoryError,
    Product,
    ProductNotFoundError,
    ProductSnapshot,
)
from audit_trail_records.domain.interfaces import AuditTrailCaretaker, ProductRepository


class InMemoryProductRepository(ProductRepository):
    def __init__(self) -> None:
        self._products: dict[str, Product] = {}

    def save(self, product: Product) -> None:
        self._products[product.product_id] = product

    def find_by_id(self, product_id: str) -> Product | None:
        return self._products.get(product_id)


class InMemoryAuditTrailCaretaker(AuditTrailCaretaker):
    def __init__(self) -> None:
        self._snapshots: dict[str, list[ProductSnapshot]] = {}

    def save(self, product_id: str, snapshot: ProductSnapshot) -> None:
        self._snapshots.setdefault(product_id, []).append(snapshot)

    def undo(self, product_id: str) -> ProductSnapshot:
        history = self._snapshots.get(product_id, [])
        if len(history) < 2:
            raise NoHistoryError(product_id)
        history.pop()
        return history[-1]

    def history(self, product_id: str) -> list[ProductSnapshot]:
        return list(self._snapshots.get(product_id, []))


@pytest.fixture
def repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


@pytest.fixture
def caretaker() -> InMemoryAuditTrailCaretaker:
    return InMemoryAuditTrailCaretaker()


def test_create_product_saves_first_snapshot(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    use_case = CreateProductUseCase(repository, caretaker)

    product = use_case.execute(
        CreateProductInput(
            product_id="p1", name="Widget", price=9.99, stock=10, changed_by="ana"
        )
    )

    assert product.current_version == 1
    assert caretaker.history("p1")[0].changed_by == "ana"


def test_update_product_increments_version_and_snapshots(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    create = CreateProductUseCase(repository, caretaker)
    create.execute(
        CreateProductInput(
            product_id="p1", name="Widget", price=9.99, stock=10, changed_by="ana"
        )
    )

    update = UpdateProductUseCase(repository, caretaker)
    product = update.execute(
        UpdateProductInput(
            product_id="p1", name="Widget v2", price=12.0, stock=5, changed_by="bob"
        )
    )

    assert product.current_version == 2
    assert product.name == "Widget v2"
    assert [snap.version for snap in caretaker.history("p1")] == [1, 2]


def test_update_product_raises_when_missing(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    update = UpdateProductUseCase(repository, caretaker)

    with pytest.raises(ProductNotFoundError):
        update.execute(
            UpdateProductInput(
                product_id="unknown", name="x", price=1.0, stock=1, changed_by="ana"
            )
        )


def test_undo_product_reverts_to_previous_snapshot(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    create = CreateProductUseCase(repository, caretaker)
    create.execute(
        CreateProductInput(
            product_id="p1", name="Widget", price=9.99, stock=10, changed_by="ana"
        )
    )
    update = UpdateProductUseCase(repository, caretaker)
    update.execute(
        UpdateProductInput(
            product_id="p1", name="Widget v2", price=12.0, stock=5, changed_by="bob"
        )
    )

    undo = UndoProductUseCase(repository, caretaker)
    product = undo.execute("p1")

    assert product.name == "Widget"
    assert product.current_version == 1


def test_undo_product_raises_when_missing(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    undo = UndoProductUseCase(repository, caretaker)

    with pytest.raises(ProductNotFoundError):
        undo.execute("unknown")


def test_get_audit_history_returns_all_snapshots(
    repository: InMemoryProductRepository, caretaker: InMemoryAuditTrailCaretaker
) -> None:
    create = CreateProductUseCase(repository, caretaker)
    create.execute(
        CreateProductInput(
            product_id="p1", name="Widget", price=9.99, stock=10, changed_by="ana"
        )
    )

    get_history = GetAuditHistoryUseCase(caretaker)
    history = get_history.execute("p1")

    assert len(history) == 1
