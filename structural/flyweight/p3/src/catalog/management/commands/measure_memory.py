"""Management command: measure_memory

Prints the Flyweight memory economy: unique ProductType count vs. total
products, and the estimated bytes saved by sharing intrinsic state.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from catalog.application.use_cases import GetFactoryStatsUseCase
from catalog.infrastructure.factory import ProductTypeFactory
from catalog.infrastructure.repository import DjangoProductRepository


class Command(BaseCommand):
    help = "Measure Flyweight memory economy by comparing with vs. without sharing."

    def handle(self, *args: object, **options: object) -> None:
        factory = ProductTypeFactory()
        factory.load_all_from_definitions()
        repository = DjangoProductRepository(factory=factory)
        stats = GetFactoryStatsUseCase(factory=factory, repository=repository).execute()

        self.stdout.write(f"Unique ProductType flyweights: {stats.unique_types}")
        self.stdout.write(f"Total products in DB:          {stats.total_products}")
        self.stdout.write(f"Sharing ratio:                 {stats.sharing_ratio:.1f}:1")
        self.stdout.write(
            f"Bytes without Flyweight:       "
            f"{stats.estimated_bytes_without_flyweight:,}"
        )
        self.stdout.write(
            f"Bytes with Flyweight:          {stats.estimated_bytes_with_flyweight:,}"
        )
        self.stdout.write(
            f"Memory saved:                  {stats.memory_saved_bytes:,} bytes "
            f"({stats.savings_percentage:.1f}%)"
        )
