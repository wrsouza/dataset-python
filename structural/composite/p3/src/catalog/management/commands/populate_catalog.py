"""Management command: populate_catalog

Creates a 3-level category tree with products at every level,
demonstrating a real e-commerce hierarchy:

  Electronics (L1)
    ├── Smartphones (L2)
    │     ├── Android (L3) — products
    │     └── iOS (L3) — products
    └── Laptops (L2)
          ├── Gaming (L3) — products
          └── Business (L3) — products

  Clothing (L1)
    ├── Men (L2)
    │     ├── T-Shirts (L3) — products
    │     └── Pants (L3) — products
    └── Women (L2)
          ├── Dresses (L3) — products
          └── Shoes (L3) — products
"""

from __future__ import annotations

from argparse import ArgumentParser
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Category, Product

TREE_DATA: list[dict] = [  # type: ignore[type-arg]
    {
        "name": "Electronics",
        "slug": "electronics",
        "children": [
            {
                "name": "Smartphones",
                "slug": "smartphones",
                "children": [
                    {
                        "name": "Android",
                        "slug": "android",
                        "products": [
                            {
                                "name": "Samsung Galaxy S24",
                                "sku": "SAM-S24",
                                "price": "999.99",
                                "stock_qty": 50,
                            },
                            {
                                "name": "Google Pixel 8",
                                "sku": "PIX-8",
                                "price": "699.99",
                                "stock_qty": 30,
                            },
                            {
                                "name": "OnePlus 12",
                                "sku": "OP-12",
                                "price": "549.99",
                                "stock_qty": 20,
                            },
                        ],
                    },
                    {
                        "name": "iOS",
                        "slug": "ios",
                        "products": [
                            {
                                "name": "iPhone 15 Pro",
                                "sku": "APL-15P",
                                "price": "1199.99",
                                "stock_qty": 80,
                            },
                            {
                                "name": "iPhone 15",
                                "sku": "APL-15",
                                "price": "799.99",
                                "stock_qty": 100,
                            },
                        ],
                    },
                ],
            },
            {
                "name": "Laptops",
                "slug": "laptops",
                "children": [
                    {
                        "name": "Gaming Laptops",
                        "slug": "gaming-laptops",
                        "products": [
                            {
                                "name": "ASUS ROG Zephyrus",
                                "sku": "ASUS-ROG-1",
                                "price": "2499.99",
                                "stock_qty": 15,
                            },
                            {
                                "name": "Razer Blade 16",
                                "sku": "RZR-B16",
                                "price": "3299.99",
                                "stock_qty": 10,
                            },
                        ],
                    },
                    {
                        "name": "Business Laptops",
                        "slug": "business-laptops",
                        "products": [
                            {
                                "name": "ThinkPad X1 Carbon",
                                "sku": "LNV-X1C",
                                "price": "1799.99",
                                "stock_qty": 25,
                            },
                            {
                                "name": "Dell XPS 13",
                                "sku": "DLL-XPS13",
                                "price": "1399.99",
                                "stock_qty": 35,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    {
        "name": "Clothing",
        "slug": "clothing",
        "children": [
            {
                "name": "Men",
                "slug": "men",
                "children": [
                    {
                        "name": "T-Shirts",
                        "slug": "men-tshirts",
                        "products": [
                            {
                                "name": "Classic White Tee",
                                "sku": "CLT-WHT-M",
                                "price": "29.99",
                                "stock_qty": 200,
                            },
                            {
                                "name": "Slim Fit Black Tee",
                                "sku": "CLT-BLK-M",
                                "price": "34.99",
                                "stock_qty": 150,
                            },
                        ],
                    },
                    {
                        "name": "Pants",
                        "slug": "men-pants",
                        "products": [
                            {
                                "name": "Slim Chino",
                                "sku": "CHN-SLM-M",
                                "price": "59.99",
                                "stock_qty": 80,
                            },
                            {
                                "name": "Classic Denim",
                                "sku": "DNM-CLS-M",
                                "price": "79.99",
                                "stock_qty": 90,
                            },
                        ],
                    },
                ],
            },
            {
                "name": "Women",
                "slug": "women",
                "children": [
                    {
                        "name": "Dresses",
                        "slug": "women-dresses",
                        "products": [
                            {
                                "name": "Summer Floral Dress",
                                "sku": "DRS-FLR-W",
                                "price": "89.99",
                                "stock_qty": 60,
                            },
                            {
                                "name": "Evening Gown",
                                "sku": "DRS-EVN-W",
                                "price": "199.99",
                                "stock_qty": 20,
                            },
                        ],
                    },
                    {
                        "name": "Shoes",
                        "slug": "women-shoes",
                        "products": [
                            {
                                "name": "Running Sneakers",
                                "sku": "SHO-RUN-W",
                                "price": "129.99",
                                "stock_qty": 100,
                            },
                            {
                                "name": "Ankle Boots",
                                "sku": "SHO-ANK-W",
                                "price": "159.99",
                                "stock_qty": 45,
                            },
                        ],
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Seed the database with a 3-level category tree and products."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing categories and products first.",
        )

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        if options.get("clear"):
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing catalog data."))

        created_categories = 0
        created_products = 0

        def create_node(
            data: dict,  # type: ignore[type-arg]
            parent: Category | None = None,
        ) -> None:
            nonlocal created_categories, created_products

            category, _ = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={"name": data["name"], "parent": parent},
            )
            created_categories += 1

            for product_data in data.get("products", []):
                Product.objects.get_or_create(
                    sku=product_data["sku"],
                    defaults={
                        "name": product_data["name"],
                        "price": Decimal(product_data["price"]),
                        "stock_qty": product_data["stock_qty"],
                        "category": category,
                    },
                )
                created_products += 1

            for child_data in data.get("children", []):
                create_node(child_data, parent=category)

        for root_data in TREE_DATA:
            create_node(root_data)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_categories} categories and "
                f"{created_products} products."
            )
        )
