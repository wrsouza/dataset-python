"""Flask application factory for the User Auth Session FSM API.

Composition root: the only place that wires the concrete Redis client
into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from auth_session_fsm.application.use_cases import (
    ExpireSessionUseCase,
    GetSessionUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshSessionUseCase,
    UnlockSessionUseCase,
)
from auth_session_fsm.domain.entities import AuthSession
from auth_session_fsm.domain.interfaces import InvalidTransitionError
from auth_session_fsm.infrastructure.factory import build_redis_client
from auth_session_fsm.infrastructure.repository import RedisSessionRepository


def _session_to_dict(session: AuthSession) -> dict[str, object]:
    return {
        "session_id": session.session_id,
        "state": session.get_current_state_name(),
        "failed_attempts": session.failed_attempts,
        "allowed_transitions": session.get_allowed_transitions(),
    }


def create_app(repository: RedisSessionRepository | None = None) -> Flask:
    """Build and configure the Flask app.

    `repository` can be injected (e.g. a fakeredis-backed repository in
    tests) so integration tests never need a real Redis instance.
    """
    app = Flask(__name__)

    session_repository = repository or RedisSessionRepository(build_redis_client())

    @app.post("/sessions/<session_id>/login")
    def login_route(session_id: str) -> tuple[Response, int]:
        payload = request.get_json(force=True)
        session = LoginUseCase(session_repository).execute(
            session_id, success=bool(payload.get("success", False))
        )
        return jsonify(_session_to_dict(session)), 200

    @app.post("/sessions/<session_id>/logout")
    def logout_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            session = LogoutUseCase(session_repository).execute(session_id)
        except InvalidTransitionError as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify(_session_to_dict(session))

    @app.post("/sessions/<session_id>/refresh")
    def refresh_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            session = RefreshSessionUseCase(session_repository).execute(session_id)
        except InvalidTransitionError as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify(_session_to_dict(session))

    @app.post("/sessions/<session_id>/expire")
    def expire_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            session = ExpireSessionUseCase(session_repository).execute(session_id)
        except InvalidTransitionError as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify(_session_to_dict(session))

    @app.post("/sessions/<session_id>/unlock")
    def unlock_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            session = UnlockSessionUseCase(session_repository).execute(session_id)
        except InvalidTransitionError as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify(_session_to_dict(session))

    @app.get("/sessions/<session_id>")
    def get_session_route(session_id: str) -> tuple[Response, int] | Response:
        session = GetSessionUseCase(session_repository).execute(session_id)
        if session is None:
            return jsonify({"error": f"Session '{session_id}' not found"}), 404
        return jsonify(_session_to_dict(session))

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
