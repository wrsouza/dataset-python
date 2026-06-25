"""Flask application entry-point for the Price Alerts service.

Composition root (DIP): the concrete Subject (KafkaPriceMonitor) and
ConcreteObservers are wired here. Use cases and the Flask routes only ever
depend on the PriceMonitor/PriceObserver abstractions from domain.interfaces.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

from flask import Flask, jsonify, request
from flask.wrappers import Response

from price_alerts.application.use_cases import (
    ListPriceAlertsUseCase,
    ProcessPriceUpdateUseCase,
    RegisterPriceAlertUseCase,
    RemovePriceAlertUseCase,
)
from price_alerts.domain.interfaces import PriceObserver
from price_alerts.infrastructure.kafka_subject import KafkaPriceMonitor
from price_alerts.infrastructure.notification_observers import (
    EmailAlertObserver,
    SmsAlertObserver,
    WebhookAlertObserver,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Composition root: concrete Subject wired here (DIP)
monitor = KafkaPriceMonitor(kafka_bootstrap=KAFKA_BOOTSTRAP)

ObserverFactory = Callable[[str], PriceObserver]

CHANNEL_FACTORIES: dict[str, ObserverFactory] = {
    "email": lambda target: EmailAlertObserver(recipient_email=target),
    "sms": lambda target: SmsAlertObserver(phone_number=target),
    "webhook": lambda target: WebhookAlertObserver(webhook_url=target),
}


def create_app() -> Flask:
    """Application factory — builds and configures the Flask app."""
    app = Flask(__name__)

    register_use_case = RegisterPriceAlertUseCase(monitor)
    remove_use_case = RemovePriceAlertUseCase(monitor)
    list_use_case = ListPriceAlertsUseCase(monitor)
    process_use_case = ProcessPriceUpdateUseCase(monitor)

    @app.post("/alerts")
    def create_alert() -> tuple[Response, int]:
        body: dict[str, Any] = request.get_json(silent=True) or {}
        channel = body.get("channel")
        target = body.get("target")
        product_id = body.get("product_id")
        threshold = body.get("threshold")

        if channel not in CHANNEL_FACTORIES:
            return jsonify({"error": f"unsupported channel '{channel}'"}), 400
        if not target or not product_id or threshold is None:
            return (
                jsonify({"error": "target, product_id and threshold are required"}),
                400,
            )

        observer = CHANNEL_FACTORIES[channel](target)
        try:
            subscription_id = register_use_case.execute(
                observer=observer,
                product_id=product_id,
                threshold=float(threshold),
            )
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return (
            jsonify(
                {
                    "subscription_id": subscription_id,
                    "observer_id": observer.observer_id,
                    "channel": channel,
                    "product_id": product_id,
                    "threshold": threshold,
                }
            ),
            201,
        )

    @app.get("/alerts")
    def list_alerts() -> Response:
        subscriptions = list_use_case.execute()
        return jsonify(
            [
                {
                    "subscription_id": sub.subscription_id,
                    "observer_id": sub.observer_id,
                    "product_id": sub.product_id,
                    "threshold": sub.threshold,
                    "is_active": sub.is_active,
                }
                for sub in subscriptions
            ]
        )

    @app.delete("/alerts/<subscription_id>")
    def delete_alert(subscription_id: str) -> tuple[Response, int]:
        remove_use_case.execute(subscription_id)
        return jsonify({"deleted": subscription_id}), 200

    @app.post("/prices/<product_id>")
    def publish_price(product_id: str) -> tuple[Response, int]:
        """Simulate an incoming price update (used when no real producer exists)."""
        body: dict[str, Any] = request.get_json(silent=True) or {}
        old_price = body.get("old_price")
        new_price = body.get("new_price")
        if old_price is None or new_price is None:
            return jsonify({"error": "old_price and new_price are required"}), 400

        process_use_case.execute(
            product_id=product_id,
            old_price=float(old_price),
            new_price=float(new_price),
        )
        return jsonify({"published": product_id}), 202

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    return app


app = create_app()


if __name__ == "__main__":
    monitor.start_consumer()
    app.run(host="0.0.0.0", port=8000)  # noqa: S104
