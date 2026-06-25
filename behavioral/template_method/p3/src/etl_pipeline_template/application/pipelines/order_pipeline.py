"""OrderETLPipeline — ConcreteClass for the order staging table.

Pre-computes `total = unit_price * quantity` so downstream consumers
of the target table never need to redo that arithmetic.
"""

from __future__ import annotations

from typing import Any

from etl_pipeline_template.domain.entities import RawRecord
from etl_pipeline_template.domain.interfaces import ETLPipeline
from etl_pipeline_template.infrastructure.repository import (
    DjangoOrderRepository,
    DjangoOrderStagingRepository,
)


class OrderETLPipeline(ETLPipeline):
    def __init__(
        self,
        staging_repository: DjangoOrderStagingRepository | None = None,
        target_repository: DjangoOrderRepository | None = None,
    ) -> None:
        self._staging_repository = staging_repository or DjangoOrderStagingRepository()
        self._target_repository = target_repository or DjangoOrderRepository()

    def extract(self) -> list[RawRecord]:
        return self._staging_repository.list_all()

    def transform(self, records: list[RawRecord]) -> list[dict[str, Any]]:
        return [
            {
                "source_id": record.source_id,
                "total": float(record.payload["unit_price"])
                * float(record.payload["quantity"]),
            }
            for record in records
        ]

    def load(self, records: list[dict[str, Any]]) -> int:
        return self._target_repository.bulk_load(records)

    def get_name(self) -> str:
        return "order_etl"
