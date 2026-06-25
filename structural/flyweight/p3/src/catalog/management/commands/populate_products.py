"""Management command: populate_products --count 10000

Demonstrates the Flyweight economy at scale: thousands of products created
while reusing only ~50 ProductType flyweight instances.
"""

from __future__ import annotations

from argparse import ArgumentParser
from typing import cast

from django.core.management.base import BaseCommand

from catalog.application.use_cases import PopulateProductsUseCase
from catalog.infrastructure.factory import ProductTypeFactory
from catalog.infrastructure.repository import DjangoProductRepository


class Command(BaseCommand):
    help = "Populate the catalog with N products distributed across ~50 ProductTypes."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--count", type=int, default=1000)

    def handle(self, *args: object, **options: object) -> None:
        count = cast(int, options["count"])

        factory = ProductTypeFactory()
        factory.load_all_from_definitions()
        repository = DjangoProductRepository(factory=factory)
        use_case = PopulateProductsUseCase(factory=factory, repository=repository)

        created = use_case.execute(count=count)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} products using "
                f"{factory.cached_count()} ProductType flyweights "
                f"(sharing ratio {created / factory.cached_count():.1f}:1)."
            )
        )
