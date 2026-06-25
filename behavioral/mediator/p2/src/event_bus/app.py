"""Flask application factory for the Event Bus API.

Composition root: the only place that wires the concrete RabbitMQ-backed
EventBus and the demo LoggingEventHandler into the use cases.
"""

from __future__ import annotations

from flask import Flask, jsonify, request
from flask.wrappers import Response

from event_bus.application.use_cases import PublishEventUseCase, SubscribeUseCase
from event_bus.domain.interfaces import EventBus
from event_bus.infrastructure.factory import build_event_bus
from event_bus.infrastructure.handlers import LoggingEventHandler


def create_app(bus: EventBus | None = None) -> Flask:
    """Build and configure the Flask app.

    `bus` can be injected (e.g. an in-memory fake bus in tests) so
    integration tests never need a real RabbitMQ broker.
    """
    app = Flask(__name__)

    event_bus = bus or build_event_bus()
    logging_handler = LoggingEventHandler()
    SubscribeUseCase(event_bus).execute("*", logging_handler)
    publish_use_case = PublishEventUseCase(event_bus)

    @app.post("/events")
    def publish_event_route() -> tuple[Response, int]:
        body = request.get_json(force=True)
        event = publish_use_case.execute(body["event_type"], body.get("payload", {}))
        return (
            jsonify(
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "published_at": event.published_at.isoformat(),
                }
            ),
            201,
        )

    @app.get("/events/log")
    def event_log_route() -> Response:
        return jsonify(
            [
                {
                    "event_type": event.event_type,
                    "payload": event.payload,
                    "published_at": event.published_at.isoformat(),
                }
                for event in logging_handler.received
            ]
        )

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=False)
