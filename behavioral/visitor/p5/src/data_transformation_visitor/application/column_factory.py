"""Builds concrete DataColumn instances from plain dict payloads."""

from __future__ import annotations

from typing import Any

from data_transformation_visitor.domain.exceptions import InvalidColumnTypeError
from data_transformation_visitor.domain.interfaces import (
    DataColumn,
    DateColumn,
    NumericColumn,
    TextColumn,
)


def build_column(payload: dict[str, Any]) -> DataColumn:
    column_type = payload.get("type", "")
    if column_type == "numeric":
        return NumericColumn(name=payload["name"], values=list(payload["values"]))
    if column_type == "text":
        return TextColumn(name=payload["name"], values=list(payload["values"]))
    if column_type == "date":
        return DateColumn(name=payload["name"], values=list(payload["values"]))
    raise InvalidColumnTypeError(column_type)


def build_columns(payloads: list[dict[str, Any]]) -> list[DataColumn]:
    return [build_column(payload) for payload in payloads]
