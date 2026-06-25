"""Core entities for the data validation pipeline domain."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ValidationStatus(StrEnum):
    """Final outcome of a record going through the validation chain."""

    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"


@dataclass
class ValidationStep:
    """A single hop the record made through the validator chain."""

    handler_name: str
    status: ValidationStatus
    reason: str
    validated_at: datetime


@dataclass
class FieldRule:
    """Describes the validation rule for a single field of a record."""

    field_name: str
    expected_type: type
    minimum: float | None = None
    maximum: float | None = None


@dataclass
class DataRecord:
    """A record submitted for validation, moving through the validator chain."""

    record_id: str
    fields: dict[str, object]
    status: ValidationStatus = ValidationStatus.PENDING
    history: list[ValidationStep] = field(default_factory=list)

    def record_step(self, step: ValidationStep) -> None:
        """Append a validation step and update the record status."""
        self.history.append(step)
        self.status = step.status
