"""Default field schema used by the Streamlit demo."""

from __future__ import annotations

from data_validation.domain.entities import FieldRule

DEFAULT_SCHEMA: list[FieldRule] = [
    FieldRule(field_name="customer_id", expected_type=str),
    FieldRule(field_name="age", expected_type=int, minimum=0, maximum=120),
    FieldRule(field_name="order_total", expected_type=float, minimum=0.0),
]
