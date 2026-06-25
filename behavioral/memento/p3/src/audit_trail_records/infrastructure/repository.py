"""Django ORM repository for the current state of a Product.

SRP: only handles product CRUD — no audit/versioning logic.
"""

from __future__ import annotations

from audit_trail_records.django_app.models import ProductModel
from audit_trail_records.domain.entities import Product
from audit_trail_records.domain.interfaces import ProductRepository


class DjangoProductRepository(ProductRepository):
    def save(self, product: Product) -> None:
        ProductModel.objects.update_or_create(
            product_id=product.product_id,
            defaults={
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "current_version": product.current_version,
            },
        )

    def find_by_id(self, product_id: str) -> Product | None:
        try:
            row = ProductModel.objects.get(product_id=product_id)
        except ProductModel.DoesNotExist:
            return None
        return Product(
            product_id=row.product_id,
            name=row.name,
            price=row.price,
            stock=row.stock,
            current_version=row.current_version,
        )
