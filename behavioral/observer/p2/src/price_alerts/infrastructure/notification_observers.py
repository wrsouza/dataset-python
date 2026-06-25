"""ConcreteObservers for the Price Alerts domain.

Each observer has exactly one responsibility (SRP):
- EmailAlertObserver   -> simulate sending an e-mail notification
- SmsAlertObserver     -> simulate sending an SMS notification
- WebhookAlertObserver -> simulate calling an external webhook URL

None of these require credentials: they log the action they would perform,
which is enough to demonstrate the Observer pattern without depending on
real third-party providers (no SMTP/SMS/HTTP creds available in this sandbox).
"""

from __future__ import annotations

import logging
import uuid

from price_alerts.domain.entities import PriceEvent
from price_alerts.domain.interfaces import PriceObserver

logger = logging.getLogger(__name__)


class EmailAlertObserver(PriceObserver):
    """Simulates sending an e-mail when a price event arrives.

    OCP: adding this channel required zero changes to PriceMonitor or to
    other observers — it is a pure extension via PriceObserver.
    """

    def __init__(self, recipient_email: str) -> None:
        self._recipient_email = recipient_email
        self._observer_id = f"email:{recipient_email}:{uuid.uuid4().hex[:8]}"
        self._sent_count = 0

    @property
    def observer_id(self) -> str:
        return self._observer_id

    def on_price_change(self, event: PriceEvent) -> None:
        self._sent_count += 1
        logger.info(
            "[EMAIL -> %s] %s changed %.2f -> %.2f (%.2f%%)",
            self._recipient_email,
            event.product_id,
            event.old_price,
            event.new_price,
            event.change_pct,
        )

    @property
    def sent_count(self) -> int:
        return self._sent_count


class SmsAlertObserver(PriceObserver):
    """Simulates sending an SMS when a price event arrives."""

    def __init__(self, phone_number: str) -> None:
        self._phone_number = phone_number
        self._observer_id = f"sms:{phone_number}:{uuid.uuid4().hex[:8]}"
        self._sent_count = 0

    @property
    def observer_id(self) -> str:
        return self._observer_id

    def on_price_change(self, event: PriceEvent) -> None:
        self._sent_count += 1
        logger.info(
            "[SMS -> %s] %s now $%.2f (%.2f%%)",
            self._phone_number,
            event.product_id,
            event.new_price,
            event.change_pct,
        )

    @property
    def sent_count(self) -> int:
        return self._sent_count


class WebhookAlertObserver(PriceObserver):
    """Simulates calling an external webhook URL with the price event payload."""

    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url
        self._observer_id = f"webhook:{webhook_url}:{uuid.uuid4().hex[:8]}"
        self._delivered_payloads: list[dict[str, object]] = []

    @property
    def observer_id(self) -> str:
        return self._observer_id

    def on_price_change(self, event: PriceEvent) -> None:
        payload: dict[str, object] = {
            "product_id": event.product_id,
            "old_price": event.old_price,
            "new_price": event.new_price,
            "change_pct": event.change_pct,
            "timestamp": event.timestamp.isoformat(),
        }
        self._delivered_payloads.append(payload)
        logger.info("[WEBHOOK -> %s] payload=%s", self._webhook_url, payload)

    @property
    def delivered_payloads(self) -> list[dict[str, object]]:
        return list(self._delivered_payloads)
