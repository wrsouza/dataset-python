"""Domain entities for the Pipeline Builder."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepType(str, Enum):
    SOURCE = "source"
    TRANSFORM = "transform"
    FILTER = "filter"
    SINK = "sink"


class TransformType(str, Enum):
    RENAME = "rename"
    CAST = "cast"
    AGGREGATE = "aggregate"
    SORT = "sort"
    DEDUPLICATE = "deduplicate"


class SourceFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    API = "api"


@dataclass
class PipelineStep:
    """Represents a single processing step in the pipeline."""

    step_type: StepType
    name: str
    config: dict[str, Any] = field(default_factory=dict)

    def describe(self) -> str:
        """Return human-readable description of the step."""
        return f"[{self.step_type.value.upper()}] {self.name}: {self.config}"


@dataclass
class ExecutionResult:
    """Result of executing a pipeline step or the full pipeline."""

    step_name: str
    success: bool
    rows_in: int = 0
    rows_out: int = 0
    preview: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    @property
    def summary(self) -> str:
        if not self.success:
            return f"{self.step_name}: FAILED — {self.error}"
        return f"{self.step_name}: OK ({self.rows_in} in → {self.rows_out} out)"


@dataclass
class Pipeline:
    """Product: a fully assembled data pipeline ready for execution."""

    name: str
    source_format: SourceFormat
    steps: list[PipelineStep] = field(default_factory=list)

    def execute(self, data: list[dict[str, Any]]) -> list[ExecutionResult]:
        """Execute all steps sequentially and return per-step results."""
        results: list[ExecutionResult] = []
        current = list(data)

        for step in self.steps:
            result = _apply_step(step, current)
            results.append(result)
            if result.success:
                current = result.preview
            else:
                # Stop pipeline on first failure
                break

        return results

    def describe(self) -> list[str]:
        return [s.describe() for s in self.steps]


# ---------------------------------------------------------------------------
# Internal step-execution helpers (kept small — SRP per function)
# ---------------------------------------------------------------------------

def _apply_step(step: PipelineStep, data: list[dict[str, Any]]) -> ExecutionResult:
    """Dispatch a step to the appropriate handler."""
    handlers = {
        StepType.SOURCE: _handle_source,
        StepType.TRANSFORM: _handle_transform,
        StepType.FILTER: _handle_filter,
        StepType.SINK: _handle_sink,
    }
    handler = handlers.get(step.step_type)
    if handler is None:
        return ExecutionResult(step_name=step.name, success=False, error="Unknown step type")
    return handler(step, data)


def _handle_source(step: PipelineStep, data: list[dict[str, Any]]) -> ExecutionResult:
    """Source step: returns the data as-is (already loaded by builder)."""
    return ExecutionResult(
        step_name=step.name,
        success=True,
        rows_in=len(data),
        rows_out=len(data),
        preview=data[:10],
    )


def _handle_transform(step: PipelineStep, data: list[dict[str, Any]]) -> ExecutionResult:
    """Transform step: rename columns, cast types, sort, deduplicate, aggregate."""
    transform_type = step.config.get("type", "")
    try:
        result_data = _apply_transform(transform_type, step.config, data)
        return ExecutionResult(
            step_name=step.name,
            success=True,
            rows_in=len(data),
            rows_out=len(result_data),
            preview=result_data[:10],
        )
    except Exception as exc:
        return ExecutionResult(step_name=step.name, success=False, error=str(exc))


def _handle_filter(step: PipelineStep, data: list[dict[str, Any]]) -> ExecutionResult:
    """Filter step: keep rows matching a simple condition."""
    condition = step.config.get("condition", "")
    try:
        filtered = _apply_filter(condition, data)
        return ExecutionResult(
            step_name=step.name,
            success=True,
            rows_in=len(data),
            rows_out=len(filtered),
            preview=filtered[:10],
        )
    except Exception as exc:
        return ExecutionResult(step_name=step.name, success=False, error=str(exc))


def _handle_sink(step: PipelineStep, data: list[dict[str, Any]]) -> ExecutionResult:
    """Sink step: simulates writing output (returns data unchanged)."""
    return ExecutionResult(
        step_name=step.name,
        success=True,
        rows_in=len(data),
        rows_out=len(data),
        preview=data[:10],
    )


def _apply_transform(
    transform_type: str,
    config: dict[str, Any],
    data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply the requested transform to the dataset."""
    if transform_type == TransformType.RENAME:
        mapping: dict[str, str] = config.get("mapping", {})
        return [{mapping.get(k, k): v for k, v in row.items()} for row in data]

    if transform_type == TransformType.SORT:
        column: str = config.get("column", "")
        reverse: bool = config.get("descending", False)
        return sorted(data, key=lambda r: r.get(column, ""), reverse=reverse)

    if transform_type == TransformType.DEDUPLICATE:
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for row in data:
            key = str(sorted(row.items()))
            if key not in seen:
                seen.add(key)
                unique.append(row)
        return unique

    if transform_type == TransformType.CAST:
        column = config.get("column", "")
        target_type: str = config.get("target_type", "str")
        type_map: dict[str, type] = {"int": int, "float": float, "str": str}
        caster = type_map.get(target_type, str)
        return [{k: (caster(v) if k == column else v) for k, v in row.items()} for row in data]

    if transform_type == TransformType.AGGREGATE:
        group_by: str = config.get("group_by", "")
        agg_col: str = config.get("agg_column", "")
        groups: dict[Any, list[Any]] = {}
        for row in data:
            key = row.get(group_by)
            groups.setdefault(key, []).append(row.get(agg_col, 0))
        return [{group_by: k, f"sum_{agg_col}": sum(v)} for k, v in groups.items()]

    return list(data)


def _apply_filter(condition: str, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate a simple 'column op value' condition against each row.

    Supports: ==, !=, >, <, >=, <=, contains
    Example: "status == active" or "amount > 100"
    """
    if not condition.strip():
        return list(data)

    for operator in (">=", "<=", "!=", "==", ">", "<", "contains"):
        if operator in condition:
            parts = condition.split(operator, 1)
            if len(parts) == 2:
                col = parts[0].strip()
                val = parts[1].strip().strip("'\"")
                return _filter_rows(data, col, operator, val)

    return list(data)


def _filter_rows(
    data: list[dict[str, Any]],
    col: str,
    operator: str,
    val: str,
) -> list[dict[str, Any]]:
    """Apply a single comparison filter to each row."""
    result: list[dict[str, Any]] = []
    for row in data:
        cell = row.get(col)
        if cell is None:
            continue
        try:
            cell_f = float(str(cell))
            val_f = float(val)
            keep = _compare_numeric(cell_f, operator, val_f)
        except ValueError:
            keep = _compare_string(str(cell), operator, val)
        if keep:
            result.append(row)
    return result


def _compare_numeric(cell: float, operator: str, val: float) -> bool:
    ops: dict[str, Any] = {
        "==": cell == val,
        "!=": cell != val,
        ">": cell > val,
        "<": cell < val,
        ">=": cell >= val,
        "<=": cell <= val,
        "contains": str(cell) in str(val),
    }
    return bool(ops.get(operator, False))


def _compare_string(cell: str, operator: str, val: str) -> bool:
    ops: dict[str, Any] = {
        "==": cell == val,
        "!=": cell != val,
        "contains": val in cell,
        ">": cell > val,
        "<": cell < val,
        ">=": cell >= val,
        "<=": cell <= val,
    }
    return bool(ops.get(operator, False))
