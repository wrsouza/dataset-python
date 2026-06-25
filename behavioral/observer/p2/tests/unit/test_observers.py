"""Unit tests for ConcreteObservers — isolated from the Subject."""

from __future__ import annotations

from price_alerts.domain.entities import PriceEvent
from price_alerts.infrastructure.notification_observers import (
    EmailAlertObserver,
    SmsAlertObserver,
    WebhookAlertObserver,
)


def _make_event(
    product_id: str = "SKU-1", old: float = 100.0, new: float = 110.0
) -> PriceEvent:
    return PriceEvent.from_prices(product_id, old, new)


def test_email_observer_increments_sent_count() -> None:
    observer = EmailAlertObserver(recipient_email="buyer@example.com")
    event = _make_event()

    observer.on_price_change(event)
    observer.on_price_change(event)

    assert observer.sent_count == 2


def test_email_observer_id_contains_recipient() -> None:
    observer = EmailAlertObserver(recipient_email="buyer@example.com")
    assert "buyer@example.com" in observer.observer_id


def test_sms_observer_increments_sent_count() -> None:
    observer = SmsAlertObserver(phone_number="+15550000")
    event = _make_event()

    observer.on_price_change(event)

    assert observer.sent_count == 1


def test_webhook_observer_records_payload() -> None:
    observer = WebhookAlertObserver(webhook_url="https://example.com/hook")
    event = _make_event(product_id="SKU-2", old=50.0, new=45.0)

    observer.on_price_change(event)

    assert len(observer.delivered_payloads) == 1
    payload = observer.delivered_payloads[0]
    assert payload["product_id"] == "SKU-2"
    assert payload["old_price"] == 50.0
    assert payload["new_price"] == 45.0


def test_each_observer_has_unique_observer_id() -> None:
    obs1 = EmailAlertObserver(recipient_email="a@example.com")
    obs2 = EmailAlertObserver(recipient_email="a@example.com")
    assert obs1.observer_id != obs2.observer_id
