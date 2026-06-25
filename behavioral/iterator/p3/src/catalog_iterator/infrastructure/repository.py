"""Django ORM-backed implementation of ProductRepository.

Uses keyset pagination (`id > cursor`) instead of `OFFSET`, so each
chunk is fetched with a single indexed query — the whole point of a
*lazy* queryset iterator: the database never materialises rows the
client hasn't asked for yet.
"""

from __future__ import annotations

from catalog_iterator.domain.entities import Product
from catalog_iterator.domain.interfaces import ProductRepository
from catalog_iterator.infrastructure.models import ProductModel


class DjangoProductRepository(ProductRepository):
    """Fetches products chunk by chunk using `id` as a keyset cursor."""

    def fetch_chunk(
        self, cursor: str | None, limit: int
    ) -> tuple[list[Product], str | None]:
        last_id = int(cursor) if cursor is not None else 0
        rows = list(ProductModel.objects.filter(id__gt=last_id).order_by("id")[:limit])
        products = [
            Product(
                product_id=row.id,
                name=row.name,
                price=float(row.price),
                category=row.category,
            )
            for row in rows
        ]
        next_cursor = str(products[-1].product_id) if len(products) == limit else None
        return products, next_cursor
