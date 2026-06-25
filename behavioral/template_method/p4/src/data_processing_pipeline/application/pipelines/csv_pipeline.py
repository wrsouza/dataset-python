"""CSVDataProcessingPipeline — ConcreteClass for CSV objects in S3."""

from __future__ import annotations

import csv
import io
from typing import Any

from data_processing_pipeline.domain.interfaces import (
    DataProcessingPipeline,
    ProcessedRecordRepositoryLike,
)
from data_processing_pipeline.infrastructure.s3_factory import S3ClientLike


class CSVDataProcessingPipeline(DataProcessingPipeline):
    def __init__(
        self,
        s3_client: S3ClientLike,
        bucket: str,
        key: str,
        repository: ProcessedRecordRepositoryLike | None = None,
    ) -> None:
        super().__init__(repository)
        self._s3_client = s3_client
        self._bucket = bucket
        self._key = key

    def fetch_input(self) -> bytes:
        response = self._s3_client.get_object(Bucket=self._bucket, Key=self._key)
        body = response["Body"]
        return body.read()  # type: ignore[attr-defined,no-any-return]

    def parse(self, raw: bytes) -> list[dict[str, Any]]:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        return [dict(row) for row in reader]

    def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {key: value.strip() for key, value in record.items() if value}
            for record in records
            if any(value.strip() for value in record.values())
        ]

    def get_name(self) -> str:
        return "csv_data_processing"
