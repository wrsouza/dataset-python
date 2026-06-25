"""Django views for the lazy catalog iterator — Client of the Iterator subsystem."""

from __future__ import annotations

import json
from decimal import Decimal

from django.http import HttpRequest, HttpResponse
from django.views import View

from catalog_iterator.application.use_cases import (
    ListProductsPageUseCase,
    SummarizeByCategoryUseCase,
)
from catalog_iterator.infrastructure.repository import DjangoProductRepository

_repository = DjangoProductRepository()


def _decimal_serialiser(obj: object) -> str:
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def _json(data: object, status: int = 200) -> HttpResponse:
    return HttpResponse(
        json.dumps(data, default=_decimal_serialiser),
        content_type="application/json",
        status=status,
    )


class ProductListView(View):
    """GET /products/?cursor=&limit= — one keyset-paginated page."""

    def get(self, request: HttpRequest) -> HttpResponse:
        cursor = request.GET.get("cursor")
        limit = int(request.GET.get("limit", "50"))

        use_case = ListProductsPageUseCase(repository=_repository)
        page = use_case.execute(cursor, limit)

        return _json(
            {
                "items": [
                    {
                        "product_id": p.product_id,
                        "name": p.name,
                        "price": p.price,
                        "category": p.category,
                    }
                    for p in page.items
                ],
                "next_cursor": page.next_cursor,
            }
        )


class CategorySummaryView(View):
    """GET /products/category-summary/ — aggregates the whole catalog via Iterator."""

    def get(self, request: HttpRequest) -> HttpResponse:
        use_case = SummarizeByCategoryUseCase(repository=_repository)
        summaries = use_case.execute()

        return _json(
            [
                {
                    "category": s.category,
                    "product_count": s.product_count,
                    "total_price": s.total_price,
                }
                for s in summaries
            ]
        )
