"""Use case orchestrating record validation through the chain."""

from __future__ import annotations

from data_validation.domain.entities import DataRecord
from data_validation.domain.interfaces import ValidationHandler


class ValidateRecordUseCase:
    """Routes a single record through the validation chain."""

    def __init__(self, chain: ValidationHandler) -> None:
        self._chain = chain

    def execute(self, record: DataRecord) -> DataRecord:
        return self._chain.handle(record)
