"""Flask application factory for the Report Generation Template API.

Composition root: the only place that wires the in-memory repository
into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from report_generation_template.application.generators.registry import (
    list_format_names,
)
from report_generation_template.application.use_cases import (
    GenerateReportUseCase,
    GetReportUseCase,
)
from report_generation_template.domain.entities import ReportRequest, ReportResult
from report_generation_template.domain.exceptions import (
    InvalidFormatError,
    ReportNotFoundError,
)
from report_generation_template.infrastructure.repository import (
    InMemoryReportRepository,
)


def _result_to_dict(result: ReportResult) -> dict[str, object]:
    return {
        "report_id": result.report_id,
        "format": result.format_name,
        "content": result.content,
        "row_count": result.row_count,
        "generated_at": result.generated_at.isoformat(),
    }


def create_app(repository: InMemoryReportRepository | None = None) -> Flask:
    """Build and configure the Flask app.

    `repository` can be injected (e.g. a fresh repository per test) so
    tests never leak state between runs.
    """
    app = Flask(__name__)

    report_repository = repository or InMemoryReportRepository()

    @app.post("/reports")
    def generate_report_route() -> tuple[Response, int] | Response:
        payload = request.get_json(force=True)
        use_case = GenerateReportUseCase(report_repository)
        try:
            result = use_case.execute(
                payload["format"],
                ReportRequest(title=payload["title"], rows=payload.get("rows", [])),
            )
        except InvalidFormatError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_result_to_dict(result)), 201

    @app.get("/reports/<report_id>")
    def get_report_route(report_id: str) -> tuple[Response, int] | Response:
        use_case = GetReportUseCase(report_repository)
        try:
            result = use_case.execute(report_id)
        except ReportNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(_result_to_dict(result))

    @app.get("/reports/formats")
    def list_formats_route() -> Response:
        return jsonify(list_format_names())

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
