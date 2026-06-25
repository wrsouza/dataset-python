"""Django views for the catalog API.

All views use the CatalogItem interface — no isinstance() checks,
so they work uniformly for any node type (LSP / OCP).
"""

from __future__ import annotations

import json
from decimal import Decimal

from django.http import Http404, HttpRequest, HttpResponse
from django.views import View

from catalog.domain.exceptions import CatalogItemNotFoundError
from catalog.domain.interfaces import CatalogItem
from catalog.infrastructure.repository import (
    build_full_catalog_tree,
    build_subtree_by_slug,
)


def _get_subtree_or_404(slug: str) -> CatalogItem:
    """Resolve a slug to its subtree or raise Http404.

    Translates the domain exception to Django's HTTP-layer Http404 —
    keeps the domain exception framework-agnostic.
    """
    node = build_subtree_by_slug(slug)
    if node is None:
        raise Http404(str(CatalogItemNotFoundError(slug)))
    return node


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


class CategoryListView(View):
    """GET /categories/ — return the full catalog tree."""

    def get(self, request: HttpRequest) -> HttpResponse:
        roots = build_full_catalog_tree()
        return _json([root.to_dict() for root in roots])


class CategoryDetailView(View):
    """GET /categories/<slug>/ — return the subtree rooted at slug."""

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        node = _get_subtree_or_404(slug)
        return _json(node.to_dict())


class CategoryProductsView(View):
    """GET /categories/<slug>/products/ — all products recursively."""

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        node = _get_subtree_or_404(slug)

        products = node.get_all_products()
        payload = [
            {
                "name": p.name,
                "sku": p.sku,
                "price": str(p.price),
                "stock_qty": p.stock_qty,
                "category_id": p.category_id,
            }
            for p in products
        ]
        return _json({"slug": slug, "total": len(payload), "products": payload})


class CategoryStatsView(View):
    """GET /categories/<slug>/stats/ — product count and total inventory value."""

    def get(self, request: HttpRequest, slug: str) -> HttpResponse:
        node = _get_subtree_or_404(slug)

        return _json(
            {
                "slug": slug,
                "name": node.name,
                "product_count": node.get_product_count(),
                "total_value": str(node.calculate_total_value()),
            }
        )
