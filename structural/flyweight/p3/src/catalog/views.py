"""Django views for the product catalog — Client of the Flyweight subsystem."""

from __future__ import annotations

import json
from decimal import Decimal

from django.http import HttpRequest, HttpResponse
from django.views import View

from catalog.application.use_cases import GetFactoryStatsUseCase, ListProductsUseCase
from catalog.infrastructure.factory import ProductTypeFactory
from catalog.infrastructure.repository import DjangoProductRepository

# Composition root: one factory shared by every request in this process —
# the in-memory Flyweight pool persists for the lifetime of the worker.
_factory = ProductTypeFactory()
_factory.load_all_from_definitions()
_repository = DjangoProductRepository(factory=_factory)


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
    """GET /products/?page=&page_size= — paginated product listing."""

    def get(self, request: HttpRequest) -> HttpResponse:
        page = int(request.GET.get("page", "1"))
        page_size = int(request.GET.get("page_size", "20"))

        use_case = ListProductsUseCase(repository=_repository)
        products = use_case.execute(page=page, page_size=page_size)

        payload = [
            {
                "sku": product.sku,
                "name": product.name,
                "price": str(product.price),
                "stock": product.stock,
                "category": product.category,
                "brand": product.brand,
                "price_with_tax": str(product.price_with_tax),
                "flyweight_id": id(product.product_type),
            }
            for product in products
        ]
        return _json({"page": page, "page_size": page_size, "products": payload})


class FactoryStatsView(View):
    """GET /products/stats/ — Flyweight memory economy statistics."""

    def get(self, request: HttpRequest) -> HttpResponse:
        use_case = GetFactoryStatsUseCase(factory=_factory, repository=_repository)
        stats = use_case.execute()

        return _json(
            {
                "unique_types": stats.unique_types,
                "total_products": stats.total_products,
                "sharing_ratio": round(stats.sharing_ratio, 2),
                "memory": {
                    "bytes_without_flyweight": stats.estimated_bytes_without_flyweight,
                    "bytes_with_flyweight": stats.estimated_bytes_with_flyweight,
                    "bytes_saved": stats.memory_saved_bytes,
                    "savings_percentage": round(stats.savings_percentage, 2),
                },
            }
        )
