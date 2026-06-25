"""Batch extraction — bounds memory regardless of source table size."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from migration.domain.interfaces import DataExtractor, Row
from migration.infrastructure.identifiers import validate_table_name


class BatchDataExtractor(DataExtractor):
    def extract_batches(
        self, connection: Any, table: str, batch_size: int
    ) -> Iterator[list[Row]]:
        validate_table_name(table)
        cursor = connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table}")
            columns = [col[0] for col in cursor.description]
            while True:
                fetched = cursor.fetchmany(batch_size)
                if not fetched:
                    break
                yield [dict(zip(columns, row, strict=True)) for row in fetched]
        finally:
            cursor.close()
