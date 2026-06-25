"""Integration test: full validation pipeline using the default schema."""

from __future__ import annotations

from data_validation.application.use_cases import ValidateRecordUseCase
from data_validation.domain.entities import DataRecord, ValidationStatus
from data_validation.infrastructure.handlers import build_validation_chain
from data_validation.infrastructure.schema import DEFAULT_SCHEMA


def test_full_pipeline_approves_well_formed_record() -> None:
    chain = build_validation_chain(DEFAULT_SCHEMA)
    use_case = ValidateRecordUseCase(chain)

    record = DataRecord(
        record_id="r-1",
        fields={"customer_id": "cust-001", "age": 42, "order_total": 19.99},
    )
    result = use_case.execute(record)

    assert result.status == ValidationStatus.VALID
    assert result.history[-1].handler_name == "ApprovalHandler"


def test_full_pipeline_rejects_record_with_multiple_issues() -> None:
    chain = build_validation_chain(DEFAULT_SCHEMA)
    use_case = ValidateRecordUseCase(chain)

    record = DataRecord(record_id="r-2", fields={"age": 999})
    result = use_case.execute(record)

    assert result.status == ValidationStatus.INVALID
    assert result.history[0].handler_name == "RequiredFieldsHandler"
