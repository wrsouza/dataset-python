"""Unit tests for the data validation chain handlers."""

from __future__ import annotations

from data_validation.domain.entities import DataRecord, FieldRule, ValidationStatus
from data_validation.infrastructure.handlers import build_validation_chain

SCHEMA = [
    FieldRule(field_name="customer_id", expected_type=str),
    FieldRule(field_name="age", expected_type=int, minimum=0, maximum=120),
    FieldRule(field_name="order_total", expected_type=float, minimum=0.0),
]


def _record(**fields: object) -> DataRecord:
    return DataRecord(record_id="r-1", fields=fields)


def test_valid_record_is_approved() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age=30, order_total=99.9))

    assert result.status == ValidationStatus.VALID
    assert result.history[0].handler_name == "ApprovalHandler"


def test_missing_required_field_is_rejected() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age=30))

    assert result.status == ValidationStatus.INVALID
    assert result.history[0].handler_name == "RequiredFieldsHandler"
    assert "order_total" in result.history[0].reason


def test_wrong_type_is_rejected() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age="thirty", order_total=10.0))

    assert result.status == ValidationStatus.INVALID
    assert result.history[0].handler_name == "TypeCheckHandler"


def test_value_below_minimum_is_rejected() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age=-5, order_total=10.0))

    assert result.status == ValidationStatus.INVALID
    assert result.history[0].handler_name == "RangeCheckHandler"
    assert "minimum" in result.history[0].reason


def test_value_above_maximum_is_rejected() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age=200, order_total=10.0))

    assert result.status == ValidationStatus.INVALID
    assert "maximum" in result.history[0].reason


def test_required_field_check_takes_priority_over_type_check() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(age="thirty"))

    assert result.history[0].handler_name == "RequiredFieldsHandler"


def test_rule_without_range_bounds_is_skipped_by_range_handler() -> None:
    chain = build_validation_chain(SCHEMA)

    result = chain.handle(_record(customer_id="c-1", age=30, order_total=10.0))

    assert result.status == ValidationStatus.VALID
