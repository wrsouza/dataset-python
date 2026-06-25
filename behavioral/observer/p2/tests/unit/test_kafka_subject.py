"""Unit tests for KafkaPriceMonitor (ConcreteSubject).

No real Kafka broker is available in this environment, so these tests rely
on the documented fallback in `KafkaPriceMonitor._publish_to_kafka`: when the
broker is unreachable, `notify_price_change` falls back to direct in-process
fan-out (`_fan_out`), letting us validate the subscribe/unsubscribe/notify
contract deterministically.
"""

from __future__ import annotations

from price_alerts.infrastructure.kafka_subject import KafkaPriceMonitor
from price_alerts.infrastructure.notification_observers import EmailAlertObserver


def test_subscribe_returns_subscription_id(monitor: KafkaPriceMonitor) -> None:
    observer = EmailAlertObserver(recipient_email="a@example.com")
    sub_id = monitor.subscribe(observer, product_id="SKU-1", threshold=5.0)

    assert sub_id in monitor.subscriptions


def test_notify_triggers_observer_above_threshold(monitor: KafkaPriceMonitor) -> None:
    observer = EmailAlertObserver(recipient_email="a@example.com")
    monitor.subscribe(observer, product_id="SKU-1", threshold=5.0)

    monitor.notify_price_change("SKU-1", old_price=100.0, new_price=110.0)

    assert observer.sent_count == 1


def test_notify_does_not_trigger_observer_below_threshold(
    monitor: KafkaPriceMonitor,
) -> None:
    observer = EmailAlertObserver(recipient_email="a@example.com")
    monitor.subscribe(observer, product_id="SKU-1", threshold=20.0)

    monitor.notify_price_change("SKU-1", old_price=100.0, new_price=105.0)

    assert observer.sent_count == 0


def test_notify_only_affects_matching_product(monitor: KafkaPriceMonitor) -> None:
    observer = EmailAlertObserver(recipient_email="a@example.com")
    monitor.subscribe(observer, product_id="SKU-1", threshold=1.0)

    monitor.notify_price_change("SKU-OTHER", old_price=100.0, new_price=200.0)

    assert observer.sent_count == 0


def test_multiple_observers_all_notified(monitor: KafkaPriceMonitor) -> None:
    email_obs = EmailAlertObserver(recipient_email="a@example.com")
    other_obs = EmailAlertObserver(recipient_email="b@example.com")
    monitor.subscribe(email_obs, product_id="SKU-1", threshold=1.0)
    monitor.subscribe(other_obs, product_id="SKU-1", threshold=1.0)

    monitor.notify_price_change("SKU-1", old_price=100.0, new_price=110.0)

    assert email_obs.sent_count == 1
    assert other_obs.sent_count == 1


def test_unsubscribe_stops_future_notifications(monitor: KafkaPriceMonitor) -> None:
    observer = EmailAlertObserver(recipient_email="a@example.com")
    sub_id = monitor.subscribe(observer, product_id="SKU-1", threshold=1.0)

    monitor.unsubscribe(sub_id)
    monitor.notify_price_change("SKU-1", old_price=100.0, new_price=200.0)

    assert observer.sent_count == 0
    assert sub_id not in monitor.subscriptions


def test_unsubscribe_unknown_id_is_a_noop(monitor: KafkaPriceMonitor) -> None:
    monitor.unsubscribe("does-not-exist")
    assert monitor.subscriptions == {}
