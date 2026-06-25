"""Integration-style test exercising every registered transformation through
the use case, mirroring how the Streamlit app wires the selectbox."""

from __future__ import annotations

from data_transformation_visitor.application.use_cases import (
    TransformDatasetInput,
    TransformDatasetUseCase,
)
from data_transformation_visitor.infrastructure.visitors.registry import (
    list_transformation_names,
)

_COLUMNS = [
    {"type": "numeric", "name": "value", "values": [10.0, 20.0, 30.0]},
    {"type": "text", "name": "name", "values": ["Ana", "Bob"]},
    {"type": "date", "name": "date", "values": ["2026-01-15", "2026-03-20"]},
]


def test_every_registered_transformation_produces_all_columns() -> None:
    use_case = TransformDatasetUseCase()

    for name in list_transformation_names():
        result = use_case.execute(
            TransformDatasetInput(transformation_name=name, columns=_COLUMNS)
        )

        assert set(result.columns) == {"value", "name", "date"}
