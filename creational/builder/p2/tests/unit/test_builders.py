"""Unit tests for Report Builder — no HTTP, no external deps."""
from __future__ import annotations

from report_builder.application.use_cases import (
    GenerateReportUseCase,
    InventoryReportDirector,
    SalesReportDirector,
)
from report_builder.domain.entities import ChartSpec, DataTable, ReportFormat
from report_builder.infrastructure.builders import (
    CSVReportBuilder,
    ExcelReportBuilder,
    PDFReportBuilder,
)


SAMPLE_TABLE = DataTable(
    title="Test Table",
    headers=["Col A", "Col B", "Col C"],
    rows=[["row1a", "row1b", 1], ["row2a", "row2b", 2]],
)
SAMPLE_CHART = ChartSpec(
    chart_type="bar", title="Test Chart", x_labels=["Jan", "Feb"], y_values=[100.0, 200.0]
)
SAMPLE_SALES = {
    "period": "Q1 2024",
    "rows": [["2024-01-01", "Alice", "Widget", 2, 100.0]],
    "total": 100.0,
}
SAMPLE_INVENTORY = {
    "warehouse": "W1",
    "rows": [["SKU1", "Widget", "Electronics", 50, 10]],
}


class TestCSVReportBuilder:
    def test_build_produces_csv_bytes(self) -> None:
        report = (
            CSVReportBuilder()
            .set_title("My Report")
            .add_header("Header line")
            .add_data_table(SAMPLE_TABLE)
            .add_footer("Footer text")
            .build()
        )
        text = report.output.decode("utf-8")
        assert "My Report" in text
        assert "Col A" in text
        assert "row1a" in text
        assert "Footer text" in text

    def test_format_is_csv(self) -> None:
        report = CSVReportBuilder().set_title("T").from_table if False else (
            CSVReportBuilder().set_title("T").add_data_table(SAMPLE_TABLE).build()
        )
        assert report.format == ReportFormat.CSV

    def test_chart_silently_accepted(self) -> None:
        # Charts are ignored in CSV — build must still succeed
        report = (
            CSVReportBuilder()
            .set_title("T")
            .add_chart(SAMPLE_CHART)
            .add_data_table(SAMPLE_TABLE)
            .build()
        )
        assert report.output

    def test_content_type(self) -> None:
        report = CSVReportBuilder().set_title("T").add_data_table(SAMPLE_TABLE).build()
        assert report.content_type == "text/csv"

    def test_filename_uses_title(self) -> None:
        report = CSVReportBuilder().set_title("My CSV Report").add_data_table(SAMPLE_TABLE).build()
        assert "My CSV Report" in report.filename


class TestExcelReportBuilder:
    def test_build_produces_xlsx_bytes(self) -> None:
        report = (
            ExcelReportBuilder()
            .set_title("Excel Report")
            .add_header("Q1 2024")
            .add_data_table(SAMPLE_TABLE)
            .build()
        )
        # XLSX files start with PK (zip header)
        assert report.output[:2] == b"PK"

    def test_format_is_excel(self) -> None:
        report = ExcelReportBuilder().set_title("T").add_data_table(SAMPLE_TABLE).build()
        assert report.format == ReportFormat.EXCEL

    def test_content_type(self) -> None:
        report = ExcelReportBuilder().set_title("T").add_data_table(SAMPLE_TABLE).build()
        assert "spreadsheet" in report.content_type


class TestPDFReportBuilder:
    def test_build_produces_pdf_bytes(self) -> None:
        report = (
            PDFReportBuilder()
            .set_title("PDF Report")
            .add_header("Period: Q1")
            .add_data_table(SAMPLE_TABLE)
            .add_footer("End of report")
            .build()
        )
        assert report.output[:4] == b"%PDF"

    def test_format_is_pdf(self) -> None:
        report = PDFReportBuilder().set_title("T").add_data_table(SAMPLE_TABLE).build()
        assert report.format == ReportFormat.PDF


class TestSalesReportDirector:
    def test_sales_report_via_csv(self) -> None:
        director = SalesReportDirector(CSVReportBuilder())
        report = director.build(SAMPLE_SALES)
        assert "Q1 2024" in report.output.decode()

    def test_sales_report_via_excel(self) -> None:
        director = SalesReportDirector(ExcelReportBuilder())
        report = director.build(SAMPLE_SALES)
        assert report.format == ReportFormat.EXCEL

    def test_inventory_report_director(self) -> None:
        director = InventoryReportDirector(CSVReportBuilder())
        report = director.build(SAMPLE_INVENTORY)
        assert b"W1" in report.output


class TestGenerateReportUseCase:
    def test_execute_sales(self) -> None:
        use_case = GenerateReportUseCase(CSVReportBuilder())
        report = use_case.execute_sales(SAMPLE_SALES)
        assert report.title.startswith("Sales Report")

    def test_execute_inventory(self) -> None:
        use_case = GenerateReportUseCase(CSVReportBuilder())
        report = use_case.execute_inventory(SAMPLE_INVENTORY)
        assert report.title.startswith("Inventory Report")
