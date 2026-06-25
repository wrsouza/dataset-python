"""Unit tests for ListOrdersPageUseCase and ExportAllOrdersUseCase."""

from __future__ import annotations

from order_pagination.application.use_cases import (
    ExportAllOrdersUseCase,
    ListOrdersPageUseCase,
)
from tests.unit.test_cursor_iterator import FakeOrderRepository


def test_list_orders_page_returns_requested_page() -> None:
    repository = FakeOrderRepository(total=5)
    use_case = ListOrdersPageUseCase(repository)

    page = use_case.execute(cursor=None, limit=2)

    assert [o.order_id for o in page.items] == [1, 2]
    assert page.next_cursor == "2"


def test_list_orders_page_last_page_has_no_next_cursor() -> None:
    repository = FakeOrderRepository(total=3)
    use_case = ListOrdersPageUseCase(repository)

    page = use_case.execute(cursor="2", limit=5)

    assert [o.order_id for o in page.items] == [3]
    assert page.next_cursor is None


def test_export_all_orders_yields_every_order_in_order() -> None:
    repository = FakeOrderRepository(total=12)
    use_case = ExportAllOrdersUseCase(repository, page_size=5)

    exported = list(use_case.execute())

    assert [o.order_id for o in exported] == list(range(1, 13))


def test_export_all_orders_with_empty_collection_yields_nothing() -> None:
    repository = FakeOrderRepository(total=0)
    use_case = ExportAllOrdersUseCase(repository)

    assert list(use_case.execute()) == []
