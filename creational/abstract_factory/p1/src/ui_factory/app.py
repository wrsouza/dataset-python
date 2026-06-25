"""Flask application entry point for the UI Component Factory API.

Composition root: this is the only module that imports concrete factories.
All other modules depend on abstractions (UIComponentFactory, UsageLogRepository).
"""
from __future__ import annotations

import os

from flask import Flask, jsonify
from flask.wrappers import Response

from ui_factory.application.use_cases import ListUsageLogsUseCase, RenderUIFamilyUseCase
from ui_factory.infrastructure.factories import (
    PostgreSQLUsageLogRepository,
    get_factory_for_platform,
)

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://app:secret@db:5432/appdb",
)


def _build_log_repository() -> PostgreSQLUsageLogRepository:
    """Instantiate the concrete repository (infrastructure concern)."""
    return PostgreSQLUsageLogRepository(database_url=DATABASE_URL)


@app.get("/components/<platform>")
def get_components(platform: str) -> Response:
    """Render the full UI component family for the requested platform.

    DIP: this route depends on UIComponentFactory (abstraction) via use case.
    OCP: adding a new platform never requires modifying this route.

    Returns 200 with component JSON, or 400 for unsupported platforms.
    """
    try:
        factory = get_factory_for_platform(platform)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400  # type: ignore[return-value]

    use_case = RenderUIFamilyUseCase(
        factory=factory,
        log_repository=_build_log_repository(),
    )
    result = use_case.execute()
    return jsonify(result.to_dict())


@app.get("/logs")
def get_logs() -> Response:
    """Return all component usage logs stored in PostgreSQL."""
    use_case = ListUsageLogsUseCase(log_repository=_build_log_repository())
    logs = use_case.execute()
    return jsonify({"logs": logs})


@app.get("/health")
def health() -> Response:
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "ui-component-factory"})
