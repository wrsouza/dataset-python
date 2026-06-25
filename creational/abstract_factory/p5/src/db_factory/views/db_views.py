"""Django views for the Database Connector Factory.

These are the composition roots: the only place in the HTTP layer that
imports and instantiates concrete factories. Views depend on use cases
(application layer) and inject concrete factories into them.

DIP: views receive the factory from get_factory_for_engine() — they never
     call PostgreSQLFactory() or MySQLFactory() directly in business logic.
"""

from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from db_factory.application.use_cases import (
    CheckDatabaseHealthUseCase,
    ExecuteQueryUseCase,
)
from db_factory.infrastructure.factories import get_factory_for_engine


@require_http_methods(["GET"])
def health_check(request: HttpRequest, db_type: str) -> JsonResponse:
    """GET /db/health/<db_type>/

    Returns a JSON health check result for the requested database engine.
    Always returns HTTP 200 with is_healthy=true|false rather than 5xx,
    so monitoring tools can parse the body for the actual health status.
    """
    try:
        factory = get_factory_for_engine(db_type)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    use_case = CheckDatabaseHealthUseCase(factory=factory)
    result = use_case.execute()
    return JsonResponse(result.to_dict(), status=200)


@csrf_exempt
@require_http_methods(["POST"])
def run_query(request: HttpRequest, db_type: str) -> JsonResponse:
    """POST /db/query/<db_type>/

    Body (JSON):
        {"sql": "SELECT 1", "params": {}}

    Executes the supplied SQL on the requested database engine and returns
    the rows as JSON. Only SELECT-like queries should be sent from clients;
    the view does not enforce this — it is the caller's responsibility.
    """
    try:
        factory = get_factory_for_engine(db_type)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    try:
        body: dict[str, object] = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    sql = body.get("sql", "")
    if not isinstance(sql, str) or not sql.strip():
        return JsonResponse(
            {"error": "Field 'sql' is required and must be a non-empty string."},
            status=400,
        )

    params_raw = body.get("params")
    params: dict[str, object] | None = (
        params_raw if isinstance(params_raw, dict) else None
    )

    from db_factory.domain.entities import QueryExecutionError

    use_case = ExecuteQueryUseCase(factory=factory)
    try:
        result = use_case.execute(sql=sql, params=params)
    except QueryExecutionError as exc:
        return JsonResponse({"error": str(exc)}, status=422)

    return JsonResponse(result.to_dict(), status=200)
