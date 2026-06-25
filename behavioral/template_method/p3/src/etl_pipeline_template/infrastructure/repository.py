"""Django ORM repositories for the staging and target tables."""

from __future__ import annotations

from typing import Any

from etl_pipeline_template.django_app.models import (
    CustomerModel,
    CustomerStagingModel,
    OrderModel,
    OrderStagingModel,
)
from etl_pipeline_template.domain.entities import RawRecord


class DjangoCustomerStagingRepository:
    def list_all(self) -> list[RawRecord]:
        return [
            RawRecord(
                source_id=row.source_id,
                payload={"full_name": row.full_name, "email": row.email},
            )
            for row in CustomerStagingModel.objects.all()
        ]


class DjangoCustomerRepository:
    def bulk_load(self, records: list[dict[str, Any]]) -> int:
        count = 0
        for record in records:
            CustomerModel.objects.update_or_create(
                source_id=record["source_id"],
                defaults={
                    "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "email": record["email"],
                },
            )
            count += 1
        return count


class DjangoOrderStagingRepository:
    def list_all(self) -> list[RawRecord]:
        return [
            RawRecord(
                source_id=row.source_id,
                payload={"unit_price": row.unit_price, "quantity": row.quantity},
            )
            for row in OrderStagingModel.objects.all()
        ]


class DjangoOrderRepository:
    def bulk_load(self, records: list[dict[str, Any]]) -> int:
        count = 0
        for record in records:
            OrderModel.objects.update_or_create(
                source_id=record["source_id"],
                defaults={"total": record["total"]},
            )
            count += 1
        return count
