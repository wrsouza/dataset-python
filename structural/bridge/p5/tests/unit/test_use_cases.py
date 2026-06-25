"""Unit tests for the Bridge Abstraction (DataView) and use cases."""

from __future__ import annotations

import pytest

from data_view.application.use_cases import (
    DataView,
    EmptyCollectionNameError,
    ListAvailableSourcesUseCase,
    LoadReportUseCase,
    SummarizedDataView,
)
from data_view.domain.entities import QueryResult, Record
from data_view.domain.interfaces import DataSource


class FakeDataSource(DataSource):
    """Test double standing in for any concrete Implementor."""

    def __init__(self, result: QueryResult) -> None:
        self._result = result
        self.connected = False
        self.fetch_calls: list[tuple[str, dict[str, object]]] = []

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def fetch(self, collection: str, filters: dict[str, object]) -> QueryResult:
        self.fetch_calls.append((collection, filters))
        return self._result

    def source_name(self) -> str:
        return "Fake"


def test_data_view_load_delegates_to_data_source(
    sample_query_result: QueryResult,
) -> None:
    source = FakeDataSource(sample_query_result)
    view = DataView(source)

    result = view.load("customers", {"active": True})

    assert result is sample_query_result
    assert source.fetch_calls == [("customers", {"active": True})]


def test_data_view_load_connects_and_disconnects(
    sample_query_result: QueryResult,
) -> None:
    source = FakeDataSource(sample_query_result)
    view = DataView(source)

    view.load("customers", {})

    assert source.connected is False  # disconnected after load() finishes


def test_data_view_load_rejects_blank_collection_name(
    sample_query_result: QueryResult,
) -> None:
    view = DataView(FakeDataSource(sample_query_result))

    with pytest.raises(EmptyCollectionNameError):
        view.load("   ", {})


def test_data_view_source_name_delegates_to_data_source(
    sample_query_result: QueryResult,
) -> None:
    view = DataView(FakeDataSource(sample_query_result))
    assert view.source_name() == "Fake"


def test_summarized_data_view_returns_result_and_summary(
    sample_query_result: QueryResult,
) -> None:
    view = SummarizedDataView(FakeDataSource(sample_query_result))

    result, summary = view.load_with_summary("customers", {})

    assert result is sample_query_result
    assert "2 registro(s)" in summary
    assert "customers" in summary
    assert "Fake" in summary


def test_load_report_use_case_executes_via_data_view(
    sample_query_result: QueryResult,
) -> None:
    view = DataView(FakeDataSource(sample_query_result))
    use_case = LoadReportUseCase(view)

    result = use_case.execute("customers", {})

    assert result is sample_query_result


def test_list_available_sources_use_case_preserves_order(
    sample_query_result: QueryResult,
) -> None:
    views = {
        "SQL Server": DataView(FakeDataSource(sample_query_result)),
        "MongoDB": DataView(FakeDataSource(sample_query_result)),
    }
    use_case = ListAvailableSourcesUseCase(views)

    assert use_case.execute() == ["SQL Server", "MongoDB"]


def test_data_view_load_disconnects_even_on_fetch_error(
    sample_query_result: QueryResult,
) -> None:
    class FailingSource(FakeDataSource):
        def fetch(self, collection: str, filters: dict[str, object]) -> QueryResult:
            raise RuntimeError("boom")

    source = FailingSource(sample_query_result)
    view = DataView(source)

    with pytest.raises(RuntimeError):
        view.load("customers", {})

    assert source.connected is False


def test_record_fields_used_by_fake_source() -> None:
    record = Record(fields={"x": 1})
    assert record.fields == {"x": 1}
