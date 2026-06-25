"""Unit tests for the default field schema."""

from __future__ import annotations

from data_validation.infrastructure.schema import DEFAULT_SCHEMA


def test_default_schema_has_expected_fields() -> None:
    field_names = {rule.field_name for rule in DEFAULT_SCHEMA}

    assert field_names == {"customer_id", "age", "order_total"}


def test_age_rule_has_bounds() -> None:
    age_rule = next(rule for rule in DEFAULT_SCHEMA if rule.field_name == "age")

    assert age_rule.minimum == 0
    assert age_rule.maximum == 120
