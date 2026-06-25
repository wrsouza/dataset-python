"""JSONDataProcessingPipeline — ConcreteClass for JSON Lines objects in S3."""

from __future__ import annotations

import json
from typing import Any

from data_processing_pipeline.domain.interfaces import (
    DataProcessingPipeline,
    ProcessedRecordRepositoryLike,
)
from data_processing_pipeline.infrastructure.s3_factory import S3ClientLike


class JSONDataProcessingPipeline(DataProcessingPipeline):
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
        text = raw.decode("utf-8")
        return [json.loads(line) for line in text.splitlines() if line.strip()]

    def clean(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [record for record in records if record.get("id") is not None]

    def get_name(self) -> str:
        return "json_data_processing"
