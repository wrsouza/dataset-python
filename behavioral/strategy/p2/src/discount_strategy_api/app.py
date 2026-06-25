"""Flask application factory for the Discount Strategy API.

Composition root: the only place that wires the concrete DB-API
connection into the use cases.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, request
from flask.wrappers import Response

from discount_strategy_api.application.use_cases import (
    ApplyDiscountInput,
    ApplyDiscountUseCase,
    GetDiscountHistoryUseCase,
)
from discount_strategy_api.domain.entities import DiscountResult
from discount_strategy_api.domain.exceptions import InvalidStrategyError
from discount_strategy_api.infrastructure.connection_factory import build_connection
from discount_strategy_api.infrastructure.repository import DiscountHistoryRepository
from discount_strategy_api.infrastructure.strategies.registry import (
    list_strategy_names,
)


def _result_to_dict(result: DiscountResult) -> dict[str, object]:
    return {
        "strategy_name": result.strategy_name,
        "original_total": result.original_total,
        "discount_amount": result.discount_amount,
        "final_total": result.final_total,
    }


def create_app(repository: DiscountHistoryRepository | None = None) -> Flask:
    """Build and configure the Flask app.

    `repository` can be injected (e.g. a sqlite-backed repository in
    tests) so integration tests never need a real MySQL instance.
    """
    app = Flask(__name__)

    discount_repository = repository or DiscountHistoryRepository(
        build_connection(), dialect=os.environ.get("DB_DIALECT", "sqlite")
    )

    @app.post("/discounts/apply")
    def apply_discount_route() -> tuple[Response, int] | Response:
        payload = request.get_json(force=True)
        use_case = ApplyDiscountUseCase(discount_repository)
        try:
            result = use_case.execute(
                ApplyDiscountInput(
                    strategy_name=payload["strategy"],
                    original_total=payload["original_total"],
                    quantity=payload.get("quantity", 1),
                    params=payload.get("params", {}),
                )
            )
        except InvalidStrategyError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_result_to_dict(result)), 201

    @app.get("/discounts/history")
    def get_history_route() -> Response:
        use_case = GetDiscountHistoryUseCase(discount_repository)
        history = use_case.execute()
        return jsonify([_result_to_dict(r) for r in history])

    @app.get("/discounts/strategies")
    def list_strategies_route() -> Response:
        return jsonify(list_strategy_names())

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
