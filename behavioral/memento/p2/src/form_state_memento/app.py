"""Flask application factory for the Form State Save/Restore API.

Composition root: the only place that wires the concrete Redis client
into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from form_state_memento.application.use_cases import (
    GetFormHistoryUseCase,
    GetFormStateUseCase,
    SaveFormStateInput,
    SaveFormStateUseCase,
    UndoFormStateUseCase,
)
from form_state_memento.domain.entities import FormSnapshot, NoHistoryError
from form_state_memento.domain.interfaces import FormCaretaker
from form_state_memento.infrastructure.caretaker import RedisFormCaretaker
from form_state_memento.infrastructure.factory import build_redis_client


def _snapshot_to_dict(snapshot: FormSnapshot) -> dict[str, object]:
    return {
        "fields": snapshot.fields,
        "step": snapshot.step,
        "label": snapshot.label,
        "created_at": snapshot.created_at.isoformat(),
    }


def create_app(caretaker: FormCaretaker | None = None) -> Flask:
    """Build and configure the Flask app.

    `caretaker` can be injected (e.g. a fakeredis-backed caretaker in
    tests) so integration tests never need a real Redis instance.
    """
    app = Flask(__name__)

    form_caretaker = caretaker or RedisFormCaretaker(build_redis_client())

    save_state = SaveFormStateUseCase(form_caretaker)
    undo_state = UndoFormStateUseCase(form_caretaker)
    get_state = GetFormStateUseCase(form_caretaker)
    get_history = GetFormHistoryUseCase(form_caretaker)

    @app.post("/forms/<session_id>")
    def save_form_route(session_id: str) -> tuple[Response, int]:
        payload = request.get_json(force=True)
        snapshot = save_state.execute(
            SaveFormStateInput(
                session_id=session_id,
                fields=payload["fields"],
                step=payload["step"],
                label=payload.get("label", "autosave"),
            )
        )
        return jsonify(_snapshot_to_dict(snapshot)), 201

    @app.get("/forms/<session_id>")
    def get_form_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            snapshot = get_state.execute(session_id)
        except NoHistoryError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(_snapshot_to_dict(snapshot))

    @app.post("/forms/<session_id>/undo")
    def undo_form_route(session_id: str) -> tuple[Response, int] | Response:
        try:
            snapshot = undo_state.execute(session_id)
        except NoHistoryError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(_snapshot_to_dict(snapshot))

    @app.get("/forms/<session_id>/history")
    def get_history_route(session_id: str) -> Response:
        history = get_history.execute(session_id)
        return jsonify([_snapshot_to_dict(s) for s in history])

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
