"""Flask application entry point for the Report Builder."""
from __future__ import annotations

from flask import Flask, Response, jsonify, request

from report_builder.application.use_cases import GenerateReportUseCase
from report_builder.domain.entities import ReportFormat
from report_builder.infrastructure.builders import (
    CSVReportBuilder,
    ExcelReportBuilder,
    PDFReportBuilder,
)

app = Flask(__name__)

BUILDER_REGISTRY = {
    ReportFormat.CSV: CSVReportBuilder,
    ReportFormat.EXCEL: ExcelReportBuilder,
    ReportFormat.PDF: PDFReportBuilder,
}

TEMPLATES = {
    "sales": {
        "description": "Sales report — period, customer, product breakdown",
        "fields": ["period", "rows", "total"],
    },
    "inventory": {
        "description": "Inventory report — stock levels per warehouse",
        "fields": ["warehouse", "rows"],
    },
}


def _resolve_builder(fmt: str) -> object:
    try:
        report_format = ReportFormat(fmt)
    except ValueError:
        return None
    builder_class = BUILDER_REGISTRY.get(report_format)
    return builder_class() if builder_class else None


@app.post("/reports/<fmt>")
def generate_report(fmt: str) -> Response:
    """Generate a report in the requested format.

    Body JSON fields:
      - type: "sales" | "inventory"
      - data: dict with the report-specific payload
    """
    builder = _resolve_builder(fmt)
    if builder is None:
        return jsonify({"error": f"Unknown format '{fmt}'. Use: csv, excel, pdf"}), 400  # type: ignore[return-value]

    body: dict[str, object] = request.get_json(force=True) or {}
    report_type: str = str(body.get("type", "sales"))
    data: dict[str, object] = body.get("data", {})  # type: ignore[assignment]

    use_case = GenerateReportUseCase(builder)  # type: ignore[arg-type]

    if report_type == "sales":
        report = use_case.execute_sales(data)
    elif report_type == "inventory":
        report = use_case.execute_inventory(data)
    else:
        return jsonify({"error": f"Unknown report type '{report_type}'"}), 400  # type: ignore[return-value]

    return Response(
        report.output,
        mimetype=report.content_type,
        headers={"Content-Disposition": f"attachment; filename={report.filename}"},
    )


@app.get("/reports/templates")
def list_templates() -> Response:
    """List available report templates."""
    return jsonify({"templates": TEMPLATES})  # type: ignore[return-value]


@app.get("/health")
def health_check() -> Response:
    return jsonify({"status": "ok"})  # type: ignore[return-value]
