"""Flask application factory for the Task Queue System API.

Composition root: the only place that wires the concrete RabbitMQ
publisher and the invoker into the use cases.
"""

from __future__ import annotations

from dataclasses import asdict

from flask import Flask, jsonify, request
from flask.wrappers import Response

from task_command_queue.application.use_cases import (
    EnqueueTaskUseCase,
    GetTaskUseCase,
    TaskNotFoundError,
)
from task_command_queue.domain.entities import TaskRecord
from task_command_queue.domain.interfaces import TaskPublisher
from task_command_queue.infrastructure.commands import UnknownCommandError
from task_command_queue.infrastructure.factory import build_publisher
from task_command_queue.infrastructure.invoker import TaskQueueInvoker


def _record_to_dict(record: TaskRecord) -> dict[str, object]:
    data = asdict(record)
    data["status"] = record.status.value
    data["executed_at"] = record.executed_at.isoformat()
    return data


def create_app(publisher: TaskPublisher | None = None) -> Flask:
    """Build and configure the Flask app.

    `publisher` can be injected (e.g. an in-memory fake publisher in
    tests) so integration tests never need a real RabbitMQ broker.
    """
    app = Flask(__name__)

    invoker = TaskQueueInvoker()
    task_publisher = publisher or build_publisher()

    enqueue_task = EnqueueTaskUseCase(invoker, task_publisher)
    get_task = GetTaskUseCase(invoker)

    @app.post("/tasks")
    def enqueue_task_route() -> tuple[Response, int]:
        body = request.get_json(force=True)
        try:
            record = enqueue_task.execute(body["command"], body.get("payload", {}))
        except UnknownCommandError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(_record_to_dict(record)), 201

    @app.get("/tasks/<task_id>")
    def get_task_route(task_id: str) -> tuple[Response, int] | Response:
        try:
            record = get_task.execute(task_id)
        except TaskNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        return jsonify(_record_to_dict(record))

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
