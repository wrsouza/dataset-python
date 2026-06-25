"""Flask application factory for the Shopping Cart Visitors API.

Composition root: the only place that wires the concrete DB-API
connection into the use cases.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask.wrappers import Response

from shopping_cart_visitors.application.use_cases import (
    GetCartReportsUseCase,
    RunCartOperationInput,
    RunCartOperationUseCase,
)
from shopping_cart_visitors.domain.entities import CartReport
from shopping_cart_visitors.domain.exceptions import (
    InvalidItemTypeError,
    InvalidOperationError,
)
from shopping_cart_visitors.infrastructure.connection_factory import build_connection
from shopping_cart_visitors.infrastructure.repository import CartReportRepository


def _report_to_dict(report: CartReport) -> dict[str, object]:
    return {"operation": report.operation.value, "data": report.data}


def create_app(repository: CartReportRepository | None = None) -> Flask:
    """Build and configure the Flask app.

    `repository` can be injected (e.g. a sqlite-backed repository in
    tests) so integration tests never need a real MySQL instance.
    """
    app = Flask(__name__)

    cart_repository = repository or CartReportRepository(
        build_connection(), dialect=os.environ.get("DB_DIALECT", "sqlite")
    )

    @app.post("/carts/operations/<operation>")
    def run_operation_route(operation: str) -> tuple[Response, int] | Response:
        payload = request.get_json(force=True)
        use_case = RunCartOperationUseCase(cart_repository)
        try:
            report = use_case.execute(
                RunCartOperationInput(operation=operation, items=payload["items"])
            )
        except (InvalidOperationError, InvalidItemTypeError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_report_to_dict(report)), 201

    @app.get("/carts/operations/<operation>/history")
    def get_history_route(operation: str) -> tuple[Response, int] | Response:
        use_case = GetCartReportsUseCase(cart_repository)
        try:
            reports = use_case.execute(operation)
        except InvalidOperationError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify([_report_to_dict(r) for r in reports])

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
