"""Unit tests for ValidateRecordUseCase."""

from __future__ import annotations

from data_validation.application.use_cases import ValidateRecordUseCase
from data_validation.domain.entities import DataRecord, FieldRule, ValidationStatus
from data_validation.infrastructure.handlers import build_validation_chain

SCHEMA = [FieldRule(field_name="amount", expected_type=float, minimum=0.0)]


def test_execute_runs_record_through_chain() -> None:
    chain = build_validation_chain(SCHEMA)
    use_case = ValidateRecordUseCase(chain)

    result = use_case.execute(DataRecord(record_id="r-1", fields={"amount": 10.0}))

    assert result.status == ValidationStatus.VALID


def test_execute_returns_invalid_record_with_reason() -> None:
    chain = build_validation_chain(SCHEMA)
    use_case = ValidateRecordUseCase(chain)

    result = use_case.execute(DataRecord(record_id="r-2", fields={"amount": -1.0}))

    assert result.status == ValidationStatus.INVALID
    assert result.history[0].reason
