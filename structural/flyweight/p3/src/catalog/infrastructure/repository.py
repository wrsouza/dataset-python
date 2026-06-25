"""Django ORM repository — translates between domain entities and ORM models.

Only this module and factory.py know about ProductTypeModel/ProductModel;
the application layer never imports Django.
"""

from __future__ import annotations

from catalog.domain.entities import Product, ProductType
from catalog.infrastructure.factory import ProductTypeFactory
from catalog.infrastructure.models import ProductModel, ProductTypeModel


class DjangoProductRepository:
    def __init__(self, factory: ProductTypeFactory) -> None:
        self._factory = factory

    def _get_or_create_type_model(self, product_type: ProductType) -> ProductTypeModel:
        model, _ = ProductTypeModel.objects.get_or_create(
            category_name=product_type.category_name,
            brand=product_type.brand,
            shipping_class=product_type.shipping_class,
            defaults={
                "tax_rate": product_type.tax_rate,
                "return_policy": product_type.return_policy,
            },
        )
        return model

    def save(self, product: Product) -> None:
        type_model = self._get_or_create_type_model(product.product_type)
        ProductModel.objects.update_or_create(
            sku=product.sku,
            defaults={
                "name": product.name,
                "price": product.price,
                "stock": product.stock,
                "product_type": type_model,
            },
        )

    def bulk_save(self, products: list[Product]) -> None:
        type_model_cache: dict[str, ProductTypeModel] = {}
        objects_to_create = []
        for product in products:
            key = product.product_type.type_key
            if key not in type_model_cache:
                type_model_cache[key] = self._get_or_create_type_model(
                    product.product_type
                )
            objects_to_create.append(
                ProductModel(
                    name=product.name,
                    price=product.price,
                    sku=product.sku,
                    stock=product.stock,
                    product_type=type_model_cache[key],
                )
            )
        ProductModel.objects.bulk_create(objects_to_create, ignore_conflicts=True)

    def count(self) -> int:
        return ProductModel.objects.count()

    def list_paginated(self, page: int, page_size: int) -> list[Product]:
        offset = (page - 1) * page_size
        queryset = ProductModel.objects.select_related("product_type")[
            offset : offset + page_size
        ]
        return [self._to_domain(model) for model in queryset]

    def _to_domain(self, model: ProductModel) -> Product:
        product_type = self._factory.get_or_create(
            category_name=model.product_type.category_name,
            brand=model.product_type.brand,
            tax_rate=model.product_type.tax_rate,
            shipping_class=model.product_type.shipping_class,
            return_policy=model.product_type.return_policy,
        )
        return Product(
            name=model.name,
            price=model.price,
            sku=model.sku,
            stock=model.stock,
            product_type=product_type,
        )
