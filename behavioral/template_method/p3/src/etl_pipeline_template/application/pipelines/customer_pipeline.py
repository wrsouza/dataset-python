"""CustomerETLPipeline — ConcreteClass for the customer staging table.

Splits a single `full_name` field into `first_name`/`last_name`, which
is the kind of normalization a real ETL would do before loading into
a clean target schema.
"""

from __future__ import annotations

from typing import Any

from etl_pipeline_template.domain.entities import RawRecord
from etl_pipeline_template.domain.interfaces import ETLPipeline
from etl_pipeline_template.infrastructure.repository import (
    DjangoCustomerRepository,
    DjangoCustomerStagingRepository,
)


class CustomerETLPipeline(ETLPipeline):
    def __init__(
        self,
        staging_repository: DjangoCustomerStagingRepository | None = None,
        target_repository: DjangoCustomerRepository | None = None,
    ) -> None:
        self._staging_repository = (
            staging_repository or DjangoCustomerStagingRepository()
        )
        self._target_repository = target_repository or DjangoCustomerRepository()

    def extract(self) -> list[RawRecord]:
        return self._staging_repository.list_all()

    def transform(self, records: list[RawRecord]) -> list[dict[str, Any]]:
        transformed = []
        for record in records:
            full_name = str(record.payload.get("full_name", "")).strip()
            first_name, _, last_name = full_name.partition(" ")
            transformed.append(
                {
                    "source_id": record.source_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": str(record.payload.get("email", "")).strip().lower(),
                }
            )
        return transformed

    def load(self, records: list[dict[str, Any]]) -> int:
        return self._target_repository.bulk_load(records)

    def get_name(self) -> str:
        return "customer_etl"
