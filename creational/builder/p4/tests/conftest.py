"""Shared fixtures for Pipeline Builder tests."""
from __future__ import annotations

import pytest

from pipeline_builder.infrastructure.builders import (
    APIPipelineBuilder,
    CSVPipelineBuilder,
    JSONPipelineBuilder,
)

SAMPLE_CSV = "id,name,category,amount\n1,Alice,A,100\n2,Bob,B,200\n3,Alice,A,150\n4,Carol,C,300\n2,Bob,B,200"
SAMPLE_JSON = '[{"id":1,"name":"Alice","category":"A","amount":100},{"id":2,"name":"Bob","category":"B","amount":200}]'


@pytest.fixture()
def csv_builder() -> CSVPipelineBuilder:
    return CSVPipelineBuilder()


@pytest.fixture()
def json_builder() -> JSONPipelineBuilder:
    return JSONPipelineBuilder()


@pytest.fixture()
def api_builder() -> APIPipelineBuilder:
    return APIPipelineBuilder()


@pytest.fixture()
def sample_rows() -> list[dict[str, object]]:
    return [
        {"id": "1", "name": "Alice", "category": "A", "amount": "100"},
        {"id": "2", "name": "Bob", "category": "B", "amount": "200"},
        {"id": "3", "name": "Alice", "category": "A", "amount": "150"},
        {"id": "4", "name": "Carol", "category": "C", "amount": "300"},
        {"id": "2", "name": "Bob", "category": "B", "amount": "200"},
    ]
