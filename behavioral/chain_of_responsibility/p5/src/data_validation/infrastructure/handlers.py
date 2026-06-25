"""Concrete handlers: required-fields -> type-check -> range-check -> approval."""

from __future__ import annotations

from datetime import UTC, datetime

from data_validation.domain.entities import (
    DataRecord,
    FieldRule,
    ValidationStatus,
    ValidationStep,
)
from data_validation.domain.interfaces import ValidationHandler


class RequiredFieldsHandler(ValidationHandler):
    """Rejects records missing any field declared in the schema."""

    def __init__(self, rules: list[FieldRule]) -> None:
        self._rules = rules

    def _inspect(self, record: DataRecord) -> ValidationStep | None:
        missing = [
            rule.field_name
            for rule in self._rules
            if rule.field_name not in record.fields
        ]
        if not missing:
            return None
        return ValidationStep(
            handler_name=self.__class__.__name__,
            status=ValidationStatus.INVALID,
            reason=f"Missing required field(s): {', '.join(missing)}",
            validated_at=datetime.now(UTC),
        )


class TypeCheckHandler(ValidationHandler):
    """Rejects records whose field values do not match the declared type."""

    def __init__(self, rules: list[FieldRule]) -> None:
        self._rules = rules

    def _inspect(self, record: DataRecord) -> ValidationStep | None:
        for rule in self._rules:
            value = record.fields.get(rule.field_name)
            if value is not None and not isinstance(value, rule.expected_type):
                return ValidationStep(
                    handler_name=self.__class__.__name__,
                    status=ValidationStatus.INVALID,
                    reason=(
                        f"Field '{rule.field_name}' expected "
                        f"{rule.expected_type.__name__}, got {type(value).__name__}"
                    ),
                    validated_at=datetime.now(UTC),
                )
        return None


class RangeCheckHandler(ValidationHandler):
    """Rejects records whose numeric fields fall outside the declared range."""

    def __init__(self, rules: list[FieldRule]) -> None:
        self._rules = rules

    def _inspect(self, record: DataRecord) -> ValidationStep | None:
        for rule in self._rules:
            if rule.minimum is None and rule.maximum is None:
                continue
            value = record.fields.get(rule.field_name)
            if not isinstance(value, (int, float)):
                continue
            if rule.minimum is not None and value < rule.minimum:
                return self._out_of_range_step(
                    rule.field_name, value, rule.minimum, "minimum"
                )
            if rule.maximum is not None and value > rule.maximum:
                return self._out_of_range_step(
                    rule.field_name, value, rule.maximum, "maximum"
                )
        return None

    @staticmethod
    def _out_of_range_step(
        field_name: str, value: float, bound: float, bound_kind: str
    ) -> ValidationStep:
        return ValidationStep(
            handler_name=RangeCheckHandler.__name__,
            status=ValidationStatus.INVALID,
            reason=(
                f"Field '{field_name}' value {value} violates {bound_kind} of {bound}"
            ),
            validated_at=datetime.now(UTC),
        )


class ApprovalHandler(ValidationHandler):
    """Final link: approves anything that passed all prior checks."""

    def _inspect(self, record: DataRecord) -> ValidationStep | None:
        return ValidationStep(
            handler_name=self.__class__.__name__,
            status=ValidationStatus.VALID,
            reason="Passed all required-field, type, and range checks.",
            validated_at=datetime.now(UTC),
        )


def build_validation_chain(rules: list[FieldRule]) -> ValidationHandler:
    """Wire the default required -> type -> range -> approval chain."""
    required_handler = RequiredFieldsHandler(rules)
    type_handler = TypeCheckHandler(rules)
    range_handler = RangeCheckHandler(rules)
    approval_handler = ApprovalHandler()
    required_handler.set_next(type_handler).set_next(range_handler).set_next(
        approval_handler
    )
    return required_handler
